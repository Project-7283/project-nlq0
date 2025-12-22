# 2. Requirements Specification

## 2.1 User Personas

| Persona | Role | Needs |
| :--- | :--- | :--- |
| **Data Analyst (Power User)** | Uses the system to quickly prototype queries and explore data relationships. | Needs accurate SQL generation, visibility into the generated SQL for verification, and the ability to refine complex queries. |
| **Business User (Viewer)** | Managers or executives who need answers to business questions without writing code. | Needs a simple chat interface, fast responses, and clear tabular results. Does not care about the underlying SQL. |
| **System Administrator** | Manages the application infrastructure and security. | Needs logs for auditing, configuration for database connections, and assurance that PII is protected. |

## 2.2 Functional Requirements

The system shall:
1.  **FR-01 (NL-to-SQL)**: Accept natural language input and generate syntactically correct MySQL queries.
2.  **FR-02 (Execution)**: Execute generated queries against the connected database and return results.
3.  **FR-03 (Visualization)**: Display query results in a readable table format within the UI.
4.  **FR-04 (Explanation)**: Provide the generated SQL alongside the results for transparency.
5.  **FR-05 (Error Handling)**: Gracefully handle invalid queries or database errors and provide user-friendly feedback.
6.  **FR-06 (Governance)**: Automatically detect and mask sensitive columns (e.g., passwords, PII) in both the generated SQL and the result set.
7.  **FR-07 (Retry Logic)**: Automatically retry query generation if the initial SQL fails execution (Self-Correction).
8.  **FR-08 (Semantic Graph Generation)**: Provide a script (`generate_graph_for_db.py`) to automatically scan a database schema, profile its data using an LLM, and build a semantic graph JSON file for context retrieval.
9.  **FR-09 (Database Agnostic)**: Support the ability to switch the underlying database connection (e.g., from MySQL to PostgreSQL) via configuration, provided a suitable adapter exists.
10. **FR-10 (Self-Evolution)**: The system shall collect user feedback (Positive/Negative) on query results and use it to autonomously update the semantic graph (adjusting edge weights or creating virtual nodes) to improve future accuracy.

## 2.3 Non-Functional Requirements

### Performance
*   **Latency**: The system should return results for standard queries within **10 seconds** (dependent on LLM provider latency).
*   **Throughput**: The API should handle concurrent requests without crashing (managed via async processing).
*   **Graph Build Time**: The initial semantic graph generation for a medium-sized database (50 tables) should complete within **5 minutes**.

### Security
*   **Data Privacy**: Sensitive data (defined in governance policies) must never be exposed in clear text.
*   **Injection Prevention**: The system must sanitize inputs and block adversarial SQL patterns (e.g., `DROP TABLE`, `UNION` attacks).
*   **Read-Only Access**: The database connection must be restricted to SELECT privileges to prevent data modification.
*   **Profiling Security**: During the graph generation phase, sample data fetched for profiling must be masked at the source (SQL level) to prevent PII leakage into the LLM context.

### Scalability
*   **Statelessness**: The application logic should be stateless to allow horizontal scaling of the application server.
*   **Vector Store**: The ChromaDB index should support efficient retrieval even as the database schema grows.

### Usability
*   **Interface**: The UI should be intuitive, requiring no training to use.
*   **Accessibility**: The web interface should follow basic accessibility standards (readable fonts, high contrast).

## 2.4 Use Case Diagram

```mermaid
usecaseDiagram
    actor "Business User" as User
    actor "System Admin" as Admin
    
    package "NLQ System" {
        usecase "Ask Question" as UC1
        usecase "View Results" as UC2
        usecase "View Generated SQL" as UC3
        usecase "Configure Database" as UC4
        usecase "View Audit Logs" as UC5
    }

    User --> UC1
    User --> UC2
    User --> UC3
    
    Admin --> UC4
    Admin --> UC5
```
