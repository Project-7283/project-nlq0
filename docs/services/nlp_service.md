# NLP Service

## Class: `NLQIntentAnalyzer`

**File:** `src/services/nlp.py`

### Description
The `NLQIntentAnalyzer` service is responsible for analyzing the user's natural language query to extract the intent, specifically identifying the starting point, ending point, and any conditions for traversing the semantic graph.

### Dependencies
*   `src.services.inference.InferenceServiceProtocol`: Interface for LLM interaction.
*   `src.services.vector_service.GraphVectorService`: (Optional) Service for semantic search over graph nodes.
*   `src.modules.semantic_graph.SemanticGraph`: The semantic graph structure.

### Key Methods

#### `__init__(self, model: InferenceServiceProtocol, vector_service: Optional[GraphVectorService] = None)`
Initializes the analyzer with an LLM model and an optional vector service.

#### `analyze_intent(self, user_query: str, graph: SemanticGraph) -> Optional[Dict[str, Any]]`
Analyzes the user query to extract graph search parameters.

*   **Input:**
    *   `user_query`: The natural language query string.
    *   `graph`: The `SemanticGraph` object representing the database schema.
*   **Process:**
    1.  **Context Retrieval:** If `vector_service` is available, it searches for the top-k most relevant nodes (tables/columns) in the graph based on the user query. Otherwise, it uses all node names.
    2.  **Prompt Construction:** Constructs a prompt for the LLM that includes the available nodes and the user query.
    3.  **LLM Call:** Calls the LLM (e.g., Gemini) to get a structured output containing `start_node`, `end_node`, and `condition`.
    4.  **Validation:** Validates the returned JSON structure.
*   **Output:** A dictionary with keys `start_node`, `end_node`, and `condition`, or `None` if extraction fails.

### Usage Example

```python
from src.services.nlp import NLQIntentAnalyzer
from src.services.inference import GeminiService
from src.services.vector_service import GraphVectorService
from src.modules.semantic_graph import SemanticGraph

# Setup
model = GeminiService()
vector_service = GraphVectorService()
graph = SemanticGraph.load_from_json("schemas/ecommerce.json")
analyzer = NLQIntentAnalyzer(model=model, vector_service=vector_service)

# Analyze
intent = analyzer.analyze_intent("Show me all orders for user John", graph)
print(intent)
# Output: {'start_node': ['users'], 'end_node': ['orders'], 'condition': '...'}
```
