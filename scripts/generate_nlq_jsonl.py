import argparse
import json
import os
import re
from pathlib import Path
import sys
from typing import Iterator, List, Dict

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

QUESTION_PATTERN = re.compile(r"^--\s*(Q\d+):\s*(.*)$")


def iter_questions(sql_lines: List[str]) -> Iterator[Dict[str, str]]:
    current_id = None
    current_question = None
    sql_buffer: List[str] = []

    def flush_current():
        if current_id and sql_buffer:
            sql_text = "\n".join(sql_buffer).strip()
            yield {
                "id": current_id,
                "question": current_question.strip(),
                "expected_sql": sql_text,
            }

    i = 0
    total_lines = len(sql_lines)
    while i < total_lines:
        line = sql_lines[i]
        stripped = line.strip()

        match = QUESTION_PATTERN.match(stripped)
        if match:
            if current_id and sql_buffer:
                yield from flush_current()
                sql_buffer = []

            current_id = match.group(1)
            current_question = match.group(2)
            i += 1
            continue

        if current_id:
            if stripped.startswith("--") and not sql_buffer:
                i += 1
                continue

            if stripped:
                sql_buffer.append(line.rstrip())

            if stripped.endswith(";"):
                i += 1
                continue
        i += 1

    if current_id and sql_buffer:
        yield from flush_current()


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert NLQ test cases SQL file to JSONL format")
    parser.add_argument(
        "sql_file",
        type=Path,
        help="Path to nlq_test_cases.sql",
    )
    parser.add_argument(
        "output_jsonl",
        type=Path,
        help="Output path for JSONL file",
    )
    args = parser.parse_args()

    sql_text = args.sql_file.read_text(encoding="utf-8")
    lines = sql_text.splitlines()

    records = list(iter_questions(lines))

    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.output_jsonl.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False))
            f.write("\n")

    print(f"Processed {len(records)} test cases from {args.sql_file} -> {args.output_jsonl}")


if __name__ == "__main__":
    main()
