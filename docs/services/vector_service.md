# Vector Service

## Class: `GraphVectorService`

**File:** `src/services/vector_service.py`

### Description
This service manages the vector embeddings of the semantic graph nodes. It uses ChromaDB to store and retrieve node information, enabling semantic search to map user queries to graph nodes (tables/columns).

### Dependencies
*   `chromadb`: Vector database.
*   `chromadb.utils.embedding_functions.OllamaEmbeddingFunction`: Uses Ollama (e.g., `nomic-embed-text`) for generating embeddings.

### Key Methods

#### `__init__(self, collection_name="schema_nodes")`
Initializes the ChromaDB client and the embedding function.

#### `index_graph(self, graph: SemanticGraph)`
Indexes the graph nodes into ChromaDB.

*   **Process:**
    *   Iterates through all nodes in the `SemanticGraph`.
    *   Constructs a text description for each node (Type + ID + Properties).
    *   Upserts the node ID, description (document), and metadata into the ChromaDB collection.

#### `search_nodes(self, query: str, k: int = 50) -> list[str]`
Performs a semantic search to find relevant nodes.

*   **Input:** User query string.
*   **Process:**
    *   Queries the ChromaDB collection with the input text.
    *   Retrieves the top-`k` matching node IDs.
*   **Output:** A list of node IDs.
