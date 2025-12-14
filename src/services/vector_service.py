import chromadb
from chromadb.utils import embedding_functions
from src.modules.semantic_graph import SemanticGraph
import os

class GraphVectorService:
    def __init__(self, collection_name="schema_nodes"):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use Ollama for embeddings to avoid local model storage issues
        # Ensure you have pulled the model: `ollama pull nomic-embed-text`
        self.embedding_fn = embedding_functions.OllamaEmbeddingFunction(
            url="http://localhost:11434/api/embeddings",
            model_name="nomic-embed-text"
        )
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def index_graph(self, graph: SemanticGraph):
        """
        Indexes the nodes of the semantic graph into ChromaDB.
        """
        ids = []
        documents = []
        metadatas = []

        for node_id, data in graph.node_properties.items():
            node_type = data.get('type', 'unknown')
            properties = data.get('properties', {})
            
            # Construct a descriptive document for the node
            # Include table name, column name, type, and any other metadata
            description = f"{node_type}: {node_id}"
            if properties:
                # Add property values to description for better semantic matching
                props_str = ", ".join([f"{k}={v}" for k, v in properties.items() if isinstance(v, (str, int, float))])
                description += f" ({props_str})"
            
            ids.append(node_id)
            documents.append(description)
            metadatas.append({"type": node_type, **{k: str(v) for k, v in properties.items()}})

        if ids:
            # Upsert to avoid duplicates or update existing
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"Indexed {len(ids)} nodes into Vector DB.")

    def search_nodes(self, query: str, k: int = 50) -> list[str]:
        """
        Retrieves the top-k most relevant node IDs for a given query.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        # results['ids'] is a list of lists (one per query)
        if results['ids']:
            return results['ids'][0]
        return []

def retrieve_context(nl_query: str) -> str:
    # Placeholder for vector DB retrieval logic
    # You would use chromadb to fetch relevant context for the query
    return "context from vector db"
