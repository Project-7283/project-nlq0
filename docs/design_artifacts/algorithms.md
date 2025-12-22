# Key Algorithms

## 1. Semantic Graph Traversal (Context-Aware Pathfinding)

**Purpose**: To find the most logical join path between two or more tables based on the user's query context, avoiding "hallucinated" joins.

**Algorithm**: Modified Dijkstra's Algorithm

**Pseudocode**:
```python
function FindPath(Graph, StartNodes, TargetNodes, QueryContext):
    PriorityQueue pq
    for node in StartNodes:
        pq.push(cost=0, current=node, path=[node])
    
    Visited = set()
    
    while pq is not empty:
        cost, current, path = pq.pop()
        
        if current in TargetNodes:
            return path
            
        if current in Visited: continue
        Visited.add(current)
        
        for neighbor in Graph.neighbors(current):
            edge = Graph.get_edge(current, neighbor)
            
            # Context Filtering
            if edge.condition AND edge.condition NOT IN QueryContext:
                continue # Skip irrelevant relationships
                
            new_cost = cost + edge.weight
            pq.push(new_cost, neighbor, path + [neighbor])
            
    return None
```

**Complexity**: $O(E + V \log V)$ where $V$ is tables/columns and $E$ is foreign keys.

---

## 2. Retrieval Augmented Generation (RAG) for Schema

**Purpose**: To select only the relevant subset of the database schema for the LLM prompt, enabling scalability to thousands of tables.

**Algorithm**: Cosine Similarity Search

**Steps**:
1.  **Indexing (Offline)**:
    *   For each Table $T$ and Column $C$:
        *   Generate text representation: `"$Name: $Description"`
        *   Compute Vector $V = \text{EmbeddingModel}(Text)$
        *   Store $(V, ID)$ in ChromaDB.
2.  **Retrieval (Online)**:
    *   Compute Query Vector $Q = \text{EmbeddingModel}(\text{UserQuery})$
    *   Calculate Cosine Similarity $S = \frac{Q \cdot V}{||Q|| ||V||}$ for all stored vectors.
    *   Select Top-$K$ items where $S > \text{Threshold}$.

---

## 3. Graph Evolution: Positive Reinforcement

**Purpose**: To "learn" from successful queries by making their paths preferred in future traversals.

**Algorithm**: Exponential Decay of Edge Weights

**Formula**:
$$ W_{new} = W_{old} \times (1 - \alpha) $$
Where:
*   $W$ is the edge weight (Cost).
*   $\alpha$ is the learning rate (e.g., 0.05).

**Logic**:
1.  User rates query as "Positive".
2.  Identify the sequence of nodes $N_1, N_2, ..., N_k$ used in the query.
3.  For each edge $(N_i, N_{i+1})$:
    *   Update weight: `edge.weight *= 0.95`
4.  Save Graph.

**Impact**: Lower weights mean Dijkstra's algorithm will prioritize this path over others with equal topological distance but higher weights (less usage).

---

## 4. Virtual Node Pattern Mining

**Purpose**: To identify frequent complex join patterns and crystallize them into reusable "Virtual Nodes".

**Algorithm**: Frequent Itemset Mining (Simplified)

**Pseudocode**:
```python
function CheckForVirtualNode(FeedbackLogs, CurrentTables):
    # 1. Define the pattern key
    PatternKey = Sort(CurrentTables)
    
    # 2. Count occurrences in positive logs
    Count = 0
    for log in FeedbackLogs:
        if log.Rating == POSITIVE and Sort(log.Tables) == PatternKey:
            Count += 1
            
    # 3. Threshold Check
    if Count >= MIN_SUPPORT_THRESHOLD (e.g., 5):
        CreateVirtualNode(PatternKey)
```

**Virtual Node Structure**:
*   **ID**: `Virtual_TableA_TableB`
*   **Type**: `virtual`
*   **Edges**: Connected to `TableA` and `TableB` with very low weight ($0.1$).
*   **Payload**: Contains the SQL fragment (e.g., `WHERE category = 'Books'`) that defines the pattern.
