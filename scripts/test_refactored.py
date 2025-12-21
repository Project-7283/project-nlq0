
import asyncio
import os
from src.flows.nl_to_sql import process_nl_query_async
from src.utils.logging import app_logger

async def main():
    # Set dummy env vars if not present for testing
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("Warning: No LLM API keys found. This test might fail if Ollama is not running.")
    
    query = "Show me the top 5 customers by total order value"
    print(f"Testing query: {query}")
    
    try:
        sql, results = await process_nl_query_async(query)
        print(f"\nGenerated SQL:\n{sql}")
        print(f"\nResults count: {len(results) if results else 0}")
        if results:
            print(f"First result: {results[0]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
