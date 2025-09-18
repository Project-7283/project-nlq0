from src.flows.nl_to_sql import process_nl_query

test_cases = [
    'what is the seller rating of fashion hub? names are case insensitive'
]

for case in test_cases:
    sql, results = process_nl_query(case)
    if results:
        # Print column headers
        headers = results[0].keys()
        print("\t".join(headers))
        # Print each row
        for row in results:
            print("\t".join(str(row[h]) for h in headers))
    else:
        print("No results found.")