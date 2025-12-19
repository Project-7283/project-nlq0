import os
from src.services.mysql_service import MySQLService
from src.services.db_reader import DBSchemaReaderService
from src.services.schema_graph_service import SchemaGraphService
from src.services.db_profiling_service import DBProfilingService, DataGovernanceConfig
from src.services.inference import GeminiService, OpenAIService
from src.modules.semantic_graph import SemanticGraph

# filepath: init/generate_graph_for_db.py


def main():
    """
    Generate semantic graph with optional enriched profiling.
    Uses LLM-powered analysis for business context and data governance.
    """
    print("\n" + "="*80)
    print("DATABASE SEMANTIC GRAPH GENERATION")
    print("="*80)
    
    # Initialize MySQLService (reads credentials from .env or config)
    print("\n📊 Connecting to database...")
    mysql_service = MySQLService()
    db_reader = DBSchemaReaderService(mysql_service)
    
    dbname = os.getenv("MYSQL_DATABASE", "ecommerce_marketplace")
    print(f"   Database: {dbname}")
    
    # Check if profiling is enabled
    enable_profiling = os.getenv("ENABLE_DB_PROFILING", "true").lower() == "true"
    
    profiling_service = None
    if enable_profiling:
        print("\n🤖 Initializing LLM services for profiling...")
        
        # Initialize LLM services based on configuration
        light_llm_provider = os.getenv("LIGHT_LLM_PROVIDER", "openai").lower()
        heavy_llm_provider = os.getenv("HEAVY_LLM_PROVIDER", "gemini").lower()
        
        # Light LLM (for column descriptions - cheaper)
        if light_llm_provider == "openai":
            light_llm_model = os.getenv("LIGHT_LLM_MODEL", "gpt-4o-mini")
            light_llm = OpenAIService(model=light_llm_model)
            print(f"   Light LLM: OpenAI {light_llm_model}")
        elif light_llm_provider == "gemini":
            light_llm = GeminiService()
            print(f"   Light LLM: Gemini")
        else:
            # Fallback to Gemini
            light_llm = GeminiService()
            print(f"   Light LLM: Gemini (fallback)")
        
        # Heavy LLM (for business analysis - more capable)
        if heavy_llm_provider == "gemini":
            heavy_llm = GeminiService()
            print(f"   Heavy LLM: Gemini")
        elif heavy_llm_provider == "openai":
            heavy_llm_model = os.getenv("HEAVY_LLM_MODEL", "gpt-4o")
            heavy_llm = OpenAIService(model=heavy_llm_model)
            print(f"   Heavy LLM: OpenAI {heavy_llm_model}")
        else:
            # Fallback to Gemini
            heavy_llm = GeminiService()
            print(f"   Heavy LLM: Gemini (fallback)")
        
        # Initialize data governance
        print("\n🔒 Initializing data governance...")
        sensitive_csv = os.getenv("SENSITIVE_COLUMNS_CSV", "config/sensitive_keywords.csv")
        governance = DataGovernanceConfig(sensitive_keywords_csv=sensitive_csv)
        print(f"   Sensitive keywords loaded: {len(governance.sensitive_keywords)}")
        print(f"   Masking enabled: {governance.masking_enabled}")
        
        # Initialize profiling service
        profiling_service = DBProfilingService(
            db_reader=db_reader,
            mysql_service=mysql_service,
            light_llm=light_llm,
            heavy_llm=heavy_llm,
            governance_config=governance
        )
    else:
        print("\n⚠️  Profiling disabled (ENABLE_DB_PROFILING=false)")
        print("   Graph will contain schema information only")
    
    # Build graph with schema service
    print("\n🏗️  Building semantic graph...")
    graph_service = SchemaGraphService(
        db_reader=db_reader,
        dbname=dbname,
        output_dir="schemas",
        profiling_service=profiling_service
    )
    
    # Build and save
    output_path = graph_service.build_and_save(
        add_reverse_fks=True,
        enable_profiling=enable_profiling
    )
    
    print("\n" + "="*80)
    print(f"✅ SUCCESS! Semantic graph saved to: {output_path}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()