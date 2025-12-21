import os
from typing import Optional
from src.services.inference import OpenAIService, GeminiService, OllamaService
from src.services.mysql_service import MySQLService
from src.services.data_governance_service import DataGovernanceService
from src.services.vector_service import GraphVectorService
from src.services.nlp import NLQIntentAnalyzer
from src.services.sql_generation_service import SQLGenerationService
from src.modules.semantic_graph import SemanticGraph
from src.utils.logging import app_logger

class Container:
    """
    Simple Dependency Injection Container
    """
    _instance = None

    def __init__(self):
        self.config = self._load_config()
        self.services = {}
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Container()
        return cls._instance

    def _load_config(self):
        return {
            "mysql_host": os.getenv("MYSQL_HOST"),
            "mysql_user": os.getenv("MYSQL_USER"),
            "mysql_password": os.getenv("MYSQL_PASSWORD"),
            "mysql_database": os.getenv("MYSQL_DATABASE", "ecommerce_marketplace"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "gemini_api_key": os.getenv("GEMINI_API_KEY"),
            "llm_provider": os.getenv("LLM_PROVIDER", "openai").lower(),
            "llm_model": os.getenv("LLM_MODEL", "gpt-4o"),
            "graph_path": os.getenv("GRAPH_PATH", "schemas/ecommerce_marketplace.json"),
            "governance_enabled": os.getenv("DATA_GOVERNANCE_ENABLED", "true").lower() == "true",
        }

    def get_governance_service(self) -> DataGovernanceService:
        if "governance" not in self.services:
            self.services["governance"] = DataGovernanceService()
        return self.services["governance"]

    def get_mysql_service(self) -> MySQLService:
        if "mysql" not in self.services:
            self.services["mysql"] = MySQLService(
                host=self.config["mysql_host"],
                user=self.config["mysql_user"],
                password=self.config["mysql_password"],
                database=self.config["mysql_database"],
                governance_service=self.get_governance_service()
            )
        return self.services["mysql"]

    def get_inference_service(self):
        if "inference" not in self.services:
            provider = self.config["llm_provider"]
            model_name = self.config["llm_model"]
            
            if provider == "openai":
                self.services["inference"] = OpenAIService(api_key=self.config["openai_api_key"], model=model_name)
            elif provider == "gemini":
                self.services["inference"] = GeminiService(api_key=self.config["gemini_api_key"])
            elif provider == "ollama":
                self.services["inference"] = OllamaService(model=model_name)
            else:
                app_logger.warning(f"Unknown provider {provider}, falling back to OpenAI")
                self.services["inference"] = OpenAIService(api_key=self.config["openai_api_key"], model=model_name)
        return self.services["inference"]

    def get_semantic_graph(self) -> SemanticGraph:
        if "graph" not in self.services:
            self.services["graph"] = SemanticGraph.load_from_json(self.config["graph_path"])
        return self.services["graph"]

    def get_vector_service(self) -> GraphVectorService:
        if "vector" not in self.services:
            svc = GraphVectorService()
            # Index graph if needed
            # svc.index_graph(self.get_semantic_graph())
            self.services["vector"] = svc
        return self.services["vector"]

    def get_intent_analyzer(self) -> NLQIntentAnalyzer:
        if "intent_analyzer" not in self.services:
            self.services["intent_analyzer"] = NLQIntentAnalyzer(
                model=self.get_inference_service(),
                vector_service=self.get_vector_service()
            )
        return self.services["intent_analyzer"]

    def get_sql_generator(self) -> SQLGenerationService:
        if "sql_generator" not in self.services:
            self.services["sql_generator"] = SQLGenerationService(
                model=self.get_inference_service(),
                sql_service=self.get_mysql_service(),
                governance_service=self.get_governance_service()
            )
        return self.services["sql_generator"]
