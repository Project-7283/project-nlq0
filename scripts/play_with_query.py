import os
import json
from src.services.nlp import NLQIntentAnalyzer
from src.modules.semantic_graph import SemanticGraph

import dotenv

dotenv.load_dotenv()

def main():
    # Load the semantic graph from the JSON schema
    schema_path = "schemas/ecommerce_marketplace.json"
    graph = SemanticGraph.load_from_json(schema_path)

    # Get Gemini API key from environment or leave None for fallback
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    analyzer = NLQIntentAnalyzer(gemini_api_key=gemini_api_key)

    print("Enter a natural language query (type 'exit' to quit):")
    while True:
        user_query = input("> ").strip()
        if user_query.lower() == "exit":
            break
        result = analyzer.analyze_intent(user_query, graph)
        if result:
            print("Extracted Intent:")
            print(f"  Start Node: {result['start_node']}")
            print(f"  End Node:   {result['end_node']}")
            print(f"  Condition:  {result['condition']}")
            # Find and print the path as well
            cost, path, walk = graph.find_path(result['start_node'], result['end_node'], 'foreign_key,association')

            print(f"  Path: ", " -> ".join(path))
            print("Walk", walk)
        else:
            print("Could not extract intent from the query.")

if __name__ == "__main__":
    main()
