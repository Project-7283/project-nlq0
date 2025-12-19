import argparse
import json
from datetime import datetime
import os
from pathlib import Path
import sys
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.flows.nl_to_sql import process_nl_query
from src.services.mysql_service import MySQLService


def load_test_cases(jsonl_path: Path) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cases.append(json.loads(line))
    return cases


def sanitize_id(question_id: str) -> str:
    digits = "".join(ch for ch in question_id if ch.isdigit())
    return digits or question_id


def _escape_markdown(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|")


def _format_results_section(title: str, data: Any) -> List[str]:
    lines: List[str] = [f"## {title}", ""]

    if data is None:
        lines.append("_No data available._")
        lines.append("")
        return lines

    if isinstance(data, list):
        if not data:
            lines.append("_Empty result set._")
            lines.append("")
            return lines

        if all(isinstance(item, dict) for item in data):
            headers: List[str] = []
            for row in data:
                for key in row.keys():
                    if key not in headers:
                        headers.append(key)

            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

            for row in data:
                row_values = [_escape_markdown(row.get(header, "")) for header in headers]
                lines.append("| " + " | ".join(row_values) + " |")
            lines.append("")
            return lines

        # List of scalars or mixed types
        lines.append("| # | Value |")
        lines.append("| --- | --- |")
        for idx, item in enumerate(data, start=1):
            lines.append(f"| {idx} | {_escape_markdown(item)} |")
        lines.append("")
        return lines

    if isinstance(data, dict):
        lines.append("| Key | Value |")
        lines.append("| --- | --- |")
        for key, value in data.items():
            lines.append(f"| {_escape_markdown(key)} | {_escape_markdown(value)} |")
        lines.append("")
        return lines

    lines.append(_escape_markdown(data))
    lines.append("")
    return lines


def run_single_test(case: Dict[str, Any], mysql_service: MySQLService, report_dir: Path) -> Dict[str, Any]:
    question_id = case["id"]
    question = case["question"]
    expected_sql = case["expected_sql"]

    report_data: Dict[str, Any] = {
        "id": question_id,
        "question": question,
        "expected_sql": expected_sql,
    }

    try:
        expected_results = mysql_service.execute_query(expected_sql)
        report_data["expected_results"] = expected_results
    except Exception as exc:
        report_data["expected_results_error"] = str(exc)
        expected_results = None

    try:
        generated_sql, generated_results = process_nl_query(question)
        report_data["generated_sql"] = generated_sql
        report_data["generated_results"] = generated_results
    except Exception as exc:
        report_data["generated_sql_error"] = str(exc)
        generated_sql = None
        generated_results = None

    if expected_results is not None and generated_results is not None:
        report_data["result_match"] = expected_results == generated_results

    report_path = report_dir / f"{question_id}.md"
    write_report(report_path, report_data)
    return report_data


def write_report(report_path: Path, data: Dict[str, Any]) -> None:
    report_lines = [
        f"# Test {data['id']}",
        "",
        "## Question",
        data["question"],
        "",
        "## Expected SQL",
        "```sql",
        data.get("expected_sql", "N/A"),
        "```",
        "",
    ]

    if "expected_results" in data:
        report_lines.extend(_format_results_section("Expected Results", data["expected_results"]))
    elif "expected_results_error" in data:
        report_lines.extend([
            "## Expected Results Error",
            data["expected_results_error"],
            "",
        ])

    if "generated_sql" in data:
        report_lines.extend([
            "## Generated SQL",
            "```sql",
            data["generated_sql"],
            "```",
            "",
        ])
    if "generated_sql_error" in data:
        report_lines.extend([
            "## Generation Error",
            data["generated_sql_error"],
            "",
        ])

    if "generated_results" in data:
        report_lines.extend(_format_results_section("Generated Results", data["generated_results"]))
    if "result_match" in data:
        report_lines.extend([
            f"## Result Match\n{data['result_match']}",
            "",
        ])

    report_path.write_text("\n".join(report_lines), encoding="utf-8")


def write_summary(run_dir: Path, summary: List[Dict[str, Any]]) -> None:
    summary_path = run_dir / "summary.md"

    lines = [
        "# Test Run Summary",
        "",
        "| ID | Result Match | Generation Error | Execution Error | Expected Error |",
        "| --- | --- | --- | --- | --- |",
    ]

    for entry in summary:
        result_match = entry.get("result_match", "N/A")
        gen_error = entry.get("generated_sql_error", "")
        exec_error = entry.get("generated_results_error", "")
        expected_error = entry.get("expected_results_error", "")

        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown(entry.get("id", "")),
                    _escape_markdown(result_match),
                    _escape_markdown(gen_error),
                    _escape_markdown(exec_error),
                    _escape_markdown(expected_error),
                ]
            )
            + " |"
        )

    lines.append("")
    summary_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NLQ test cases against NL to SQL pipeline")
    parser.add_argument("jsonl_path", type=Path, help="Path to generated NLQ JSONL file")
    parser.add_argument("--start", type=int, default=1, help="Start question number (inclusive)")
    parser.add_argument("--end", type=int, default=None, help="End question number (inclusive)")
    parser.add_argument("--output-dir", type=Path, default=Path("reports/test_runs"), help="Base directory for test reports")
    args = parser.parse_args()

    cases = load_test_cases(args.jsonl_path)

    filtered_cases = []
    for case in cases:
        q_num = int(sanitize_id(case["id"]))
        if q_num < args.start:
            continue
        if args.end is not None and q_num > args.end:
            continue
        filtered_cases.append(case)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = args.output_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    mysql_service = MySQLService(database="ecommerce_marketplace")

    summary: List[Dict[str, Any]] = []
    for case in filtered_cases:
        result = run_single_test(case, mysql_service, run_dir)
        summary.append(result)

    write_summary(run_dir, summary)
    print(f"Saved reports in {run_dir}")


if __name__ == "__main__":
    main()
