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
    
    def _create_rich_document(self, node_id: str, node_type: str, properties: dict) -> str:
        """
        Create a semantically rich document for embedding that prioritizes important properties.
        Different node types get different formatting for optimal retrieval.
        
        Args:
            node_id: The node identifier
            node_type: Type of node (table, attribute, view, virtual_table)
            properties: Node properties dictionary
            
        Returns:
            Rich text document optimized for semantic search
        """
        if node_type == "table":
            return self._format_table_document(node_id, properties)
        elif node_type == "attribute":
            return self._format_column_document(node_id, properties)
        elif node_type == "view":
            return self._format_view_document(node_id, properties)
        elif node_type == "virtual_table":
            return self._format_virtual_table_document(node_id, properties)
        else:
            # Fallback for unknown types
            return f"{node_type}: {node_id}"
    
    def _format_table_document(self, node_id: str, properties: dict) -> str:
        """Format table node as rich document"""
        parts = [f"Table: {node_id}"]
        
        # Primary descriptive fields
        if properties.get('description'):
            parts.append(f"Description: {properties['description']}")
        
        if properties.get('business_purpose'):
            parts.append(f"Business Purpose: {properties['business_purpose']}")
        
        # Domain and impact
        if properties.get('data_domain'):
            parts.append(f"Domain: {properties['data_domain']}")
        
        if properties.get('business_impact'):
            parts.append(f"Business Impact: {properties['business_impact']}")
        
        # Table comment (often has useful info)
        if properties.get('table_comment'):
            parts.append(f"Comment: {properties['table_comment']}")
        
        # Typical queries (great for matching user intent)
        if properties.get('typical_queries') and isinstance(properties['typical_queries'], list):
            queries = properties['typical_queries'][:3]  # First 3 queries
            if queries:
                parts.append(f"Common Questions: {'; '.join(queries)}")
        
        # Related processes
        if properties.get('related_business_processes') and isinstance(properties['related_business_processes'], list):
            processes = properties['related_business_processes'][:3]
            if processes:
                parts.append(f"Related Processes: {', '.join(processes)}")
        
        # Row count (helps with data scale understanding)
        if properties.get('row_count'):
            parts.append(f"Row Count: {properties['row_count']}")
        
        return ". ".join(parts)
    
    def _format_column_document(self, node_id: str, properties: dict) -> str:
        """Format column/attribute node as rich document"""
        # Extract table and column name
        if '.' in node_id:
            table_name, col_name = node_id.rsplit('.', 1)
            parts = [f"Column: {col_name} in table {table_name}"]
        else:
            col_name = node_id
            parts = [f"Column: {col_name}"]
        
        # Type information
        if properties.get('Type'):
            parts.append(f"Type: {properties['Type']}")
        
        # Descriptive fields (most important for matching)
        if properties.get('description'):
            parts.append(f"Description: {properties['description']}")
        
        if properties.get('Comment'):
            parts.append(f"Comment: {properties['Comment']}")
        
        # Semantic meaning (helps with natural language matching)
        if properties.get('semantic_meaning'):
            parts.append(f"Semantic: {properties['semantic_meaning']}")
        
        # Business relevance
        if properties.get('business_relevance'):
            parts.append(f"Business Use: {properties['business_relevance']}")
        
        # Categorical information (helps with filtering queries)
        if properties.get('is_categorical'):
            if properties.get('sample_values') and isinstance(properties['sample_values'], list):
                samples = properties['sample_values'][:5]
                parts.append(f"Possible Values: {', '.join(map(str, samples))}")
        
        # Statistical hints
        stats = []
        if properties.get('distinct_count'):
            stats.append(f"{properties['distinct_count']} distinct values")
        if properties.get('null_percentage'):
            stats.append(f"{properties['null_percentage']}% null")
        if stats:
            parts.append(f"Statistics: {', '.join(stats)}")
        
        # Sensitivity flag (important for governance)
        if properties.get('is_sensitive'):
            parts.append("Sensitive: Yes")
        
        return ". ".join(parts)
    
    def _format_view_document(self, node_id: str, properties: dict) -> str:
        """Format view node as rich document"""
        parts = [f"View: {node_id}"]
        
        if properties.get('description'):
            parts.append(f"Description: {properties['description']}")
        
        if properties.get('view_comment'):
            parts.append(f"Comment: {properties['view_comment']}")
        
        return ". ".join(parts)
    
    def _format_virtual_table_document(self, node_id: str, properties: dict) -> str:
        """Format virtual table node as rich document"""
        parts = [f"Virtual Table: {node_id}"]
        
        if properties.get('description'):
            parts.append(f"Description: {properties['description']}")
        
        if properties.get('use_case'):
            parts.append(f"Use Case: {properties['use_case']}")
        
        return ". ".join(parts)

    def index_graph(self, graph: SemanticGraph):
        """
        Indexes the nodes of the semantic graph into ChromaDB with rich, contextual documents.
        Uses specialized formatting for different node types to optimize semantic search.
        """
        ids = []
        documents = []
        metadatas = []

        for node_id, data in graph.node_properties.items():
            node_type = data.get('type', 'unknown')
            properties = data.get('properties', {})
            
            # Create rich document using specialized formatter
            document = self._create_rich_document(node_id, node_type, properties)
            
            # Prepare metadata (flatten complex structures for ChromaDB)
            metadata = {"type": node_type, "node_id": node_id}
            
            # Add key properties to metadata for filtering
            if node_type == "table":
                if properties.get('data_domain'):
                    metadata['domain'] = properties['data_domain']
                if properties.get('business_impact'):
                    metadata['impact'] = properties['business_impact']
                if properties.get('row_count'):
                    metadata['row_count'] = str(properties['row_count'])
            elif node_type == "attribute":
                if properties.get('Type'):
                    metadata['data_type'] = properties['Type']
                if properties.get('is_sensitive'):
                    metadata['is_sensitive'] = str(properties['is_sensitive'])
                if properties.get('is_categorical'):
                    metadata['is_categorical'] = str(properties['is_categorical'])
                if properties.get('semantic_meaning'):
                    metadata['semantic_meaning'] = properties['semantic_meaning']
            
            ids.append(node_id)
            documents.append(document)
            metadatas.append(metadata)

        if ids:
            # Upsert to avoid duplicates or update existing
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"Indexed {len(ids)} nodes into Vector DB with rich contextual documents.")
            print(f"  - Tables: {sum(1 for m in metadatas if m['type'] == 'table')}")
            print(f"  - Columns: {sum(1 for m in metadatas if m['type'] == 'attribute')}")
            print(f"  - Views: {sum(1 for m in metadatas if m['type'] == 'view')}")
            print(f"  - Virtual Tables: {sum(1 for m in metadatas if m['type'] == 'virtual_table')}")

    def search_nodes(self, query: str, k: int = 50) -> list[str]:
        """
        Retrieves the top-k most relevant node IDs for a given query.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        # results['ids'] is a list of lists (one per query)
        if results['metadatas']:
            return [meta.get('node_id') for meta in results['metadatas'][0]]
        return []

def retrieve_context(nl_query: str) -> str:
    # Placeholder for vector DB retrieval logic
    # You would use chromadb to fetch relevant context for the query
    return "context from vector db"
