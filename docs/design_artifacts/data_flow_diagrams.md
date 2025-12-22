# Data Flow Diagrams (DFD)

## Level 0: Context Diagram

The highest-level view of the system, showing the interaction between the User and the NLQ System.

```mermaid
graph LR
    User[User] -- "1. Natural Language Query" --> System((NLQ System))
    System -- "2. SQL Query & Results" --> User
    User -- "3. Feedback (+/-)" --> System
    
    DB[(Database)] -- "Schema & Data" --> System
    System -- "SQL Execution" --> DB
```

---

## Level 1: Main Process Flow

Breakdown of the main system processes.

```mermaid
graph TD
    User[User] -->|Query| UI[Streamlit UI]
    
    subgraph "NLQ System"
        UI -->|Raw Query| P1(Intent Analysis)
        P1 -->|Intent & Entities| P2(SQL Generation)
        P2 -->|Generated SQL| P3(Execution & Governance)
        P3 -->|Results| UI
        
        UI -->|Feedback| P4(Evolution Engine)
        P4 -->|Updates| DS1[(Semantic Graph)]
    end
    
    DS1 -->|Context| P1
    DS1 -->|Path Info| P2
    
    P3 -->|Query| DB[(Target Database)]
    DB -->|Data| P3
```

**Processes**:
1.  **Intent Analysis**: Converts NL to structured intent using Vector Store.
2.  **SQL Generation**: Maps intent to Graph Path and generates SQL using LLM.
3.  **Execution & Governance**: Checks for PII, masks data, runs query.
4.  **Evolution Engine**: Updates graph weights based on feedback.

---

## Level 2: Query Processing (Detailed)

Drilling down into the "Query Processing" pipeline.

```mermaid
graph TD
    Input[User Query] --> Vector{Vector Search}
    Vector -->|Top-K Tables| Prompt[Build Prompt]
    Graph[(Semantic Graph)] -->|Schema Context| Prompt
    
    Prompt --> LLM[LLM Inference]
    LLM -->|Draft SQL| Parser[SQL Parser]
    
    Parser --> Gov{Governance Check}
    Gov -- "Unsafe" --> Error[Return Error]
    Gov -- "Safe" --> Exec[DB Execution]
    
    Exec --> Mask[Data Masking]
    Mask --> Output[Final Result]
```

## Level 2: Evolution Process (Detailed)

Drilling down into the "Evolution Engine".

```mermaid
graph TD
    Feedback[User Feedback] --> Log[(Feedback Logs)]
    Log --> Analyzer{Analyze Feedback}
    
    Analyzer -- "Positive" --> Weight[Weight Adjuster]
    Weight -->|Decrease Weight| Graph[(Semantic Graph)]
    
    Analyzer -- "Positive & Frequent" --> Miner[Pattern Miner]
    Miner -->|Create Node| Virtual[Virtual Node Builder]
    Virtual -->|Add Node| Graph
    
    Analyzer -- "Negative" --> RCA[Root Cause Analysis LLM]
    RCA -->|Missing Synonym| Vector[(Vector Store)]
    RCA -->|Bad Path| Penalty[Weight Penalizer]
    Penalty -->|Increase Weight| Graph
```
