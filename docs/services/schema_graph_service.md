# Schema Graph Service

## Class: `SchemaGraphService`

**File:** `src/services/schema_graph_service.py`

### Description
This service is responsible for extracting the database schema (tables, columns, foreign keys) and converting it into a `SemanticGraph` structure. This graph is then used for pathfinding and context retrieval.

### Dependencies
*   `src.services.db_reader.DBReaderProtocol`: Interface for reading database metadata.
*   `src.modules.semantic_graph.SemanticGraph`: The graph data structure.

### Key Methods

#### `__init__(self, db_reader: DBReaderProtocol, dbname: str, output_dir: str = "schemas")`
Initializes the service with a database reader and output configuration.

#### `build_graph(self)`
Constructs the semantic graph from the database schema.

*   **Nodes:**
    *   **Table Nodes:** Created for each table.
    *   **Attribute Nodes:** Created for each column, linked to their respective table nodes with "association" edges.
*   **Edges:**
    *   **Association:** Between tables and their columns.
    *   **Foreign Key:** Between tables based on foreign key constraints found in `information_schema`.

#### `add_reverse_foreign_keys(self)`
Adds reverse edges for all foreign key relationships to allow bidirectional traversal in the graph.

#### `save(self)`
Saves the constructed graph to a JSON file in the `output_dir`.

#### `build_and_save(self, add_reverse_fks=True)`
Orchestrates the build process: builds the graph, optionally adds reverse foreign keys, and saves it to disk.
