"""
Example script demonstrating DBProfilingService usage.
This shows how to profile a database with enriched LLM-powered metadata.
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.mysql_service import MySQLService
from src.services.db_reader import DBSchemaReaderService
from src.services.db_profiling_service import DBProfilingService, DataGovernanceConfig
from src.services.inference import GeminiService, OpenAIService


def main():
    """Example: Profile a single table"""
    
    print("\n" + "="*80)
    print("DB PROFILING SERVICE - EXAMPLE")
    print("="*80 + "\n")
    
    # 1. Initialize services
    print("1. Initializing services...")
    mysql_service = MySQLService()
    db_reader = DBSchemaReaderService(mysql_service)
    
    # 2. Initialize LLMs
    print("2. Initializing LLM services...")
    try:
        light_llm = OpenAIService(model="gpt-4o-mini")
        print("   ✓ Light LLM: OpenAI gpt-4o-mini")
    except Exception as e:
        print(f"   ✗ OpenAI not available: {e}")
        light_llm = GeminiService()
        print("   ✓ Light LLM: Gemini (fallback)")
    
    try:
        heavy_llm = GeminiService()
        print("   ✓ Heavy LLM: Gemini")
    except Exception as e:
        print(f"   ✗ Gemini not available: {e}")
        return
    
    # 3. Initialize governance
    print("3. Initializing data governance...")
    governance = DataGovernanceConfig(
        sensitive_keywords_csv="config/sensitive_keywords.csv"
    )
    print(f"   ✓ Loaded {len(governance.sensitive_keywords)} sensitive keywords")
    
    # 4. Create profiling service
    print("4. Creating profiling service...")
    profiling_service = DBProfilingService(
        db_reader=db_reader,
        mysql_service=mysql_service,
        light_llm=light_llm,
        heavy_llm=heavy_llm,
        governance_config=governance
    )
    
    # 5. Profile a single table (for demo)
    dbname = os.getenv("MYSQL_DATABASE", "ecommerce_marketplace")
    print(f"\n5. Profiling database: {dbname}")
    print("   (This will take a few minutes...)\n")
    
    # Get first table
    tables, views = db_reader.get_tables(dbname)
    if not tables:
        print("   ✗ No tables found!")
        return
    
    sample_table = tables[0]
    print(f"   Profiling sample table: {sample_table}\n")
    
    # Profile single table
    table_profile = profiling_service.profile_table(dbname, sample_table)
    
    # 6. Display results
    print("\n" + "="*80)
    print("PROFILING RESULTS")
    print("="*80 + "\n")
    
    print(f"Table: {sample_table}")
    print(f"Row Count: {table_profile.get('row_count', 'N/A')}")
    print(f"Table Comment: {table_profile.get('table_comment', 'None')}\n")
    
    print("Business Context:")
    print(f"  Purpose: {table_profile.get('business_purpose', 'N/A')}")
    print(f"  Domain: {table_profile.get('data_domain', 'N/A')}")
    print(f"  Impact: {table_profile.get('business_impact', 'N/A')}")
    print(f"  Description: {table_profile.get('description', 'N/A')}\n")
    
    print("Typical Queries:")
    for i, query in enumerate(table_profile.get('typical_queries', []), 1):
        print(f"  {i}. {query}")
    
    print("\nColumn Statistics (first 3 columns):")
    col_stats = table_profile.get('column_statistics', {})
    for i, (col_name, stats) in enumerate(list(col_stats.items())[:3], 1):
        print(f"\n  Column {i}: {col_name}")
        if stats.get('is_sensitive'):
            print(f"    [SENSITIVE - Masked]")
        else:
            print(f"    Distinct: {stats.get('distinct_count', 'N/A')}")
            print(f"    Null %: {stats.get('null_percentage', 'N/A')}")
            print(f"    Categorical: {stats.get('is_categorical', False)}")
            if stats.get('sample_values'):
                print(f"    Samples: {', '.join(map(str, stats['sample_values'][:5]))}")
    
    print("\nColumn Descriptions (first 3 columns):")
    col_desc = table_profile.get('column_descriptions', {})
    for i, (col_name, desc) in enumerate(list(col_desc.items())[:3], 1):
        print(f"\n  Column {i}: {col_name}")
        print(f"    Description: {desc.get('description', 'N/A')}")
        print(f"    Semantic: {desc.get('semantic_meaning', 'N/A')}")
    
    # 7. Optionally save to file
    output_file = f"profile_{sample_table}.json"
    with open(output_file, 'w') as f:
        json.dump(table_profile, f, indent=2, default=str)
    
    print(f"\n{'='*80}")
    print(f"Full profile saved to: {output_file}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
