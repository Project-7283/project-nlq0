# 7. Traceability Matrix

This matrix maps the Functional Requirements (FR) to the Design Components that implement them and the Test Cases (TC) that validate them.

| Req ID | Requirement Description | Design Component | Test Case ID |
| :--- | :--- | :--- | :--- |
| **FR-01** | **NL-to-SQL Conversion** | `NLQIntentAnalyzer`, `SQLGenerationService` | **TC-01** |
| **FR-02** | **SQL Execution** | `MySQLService` | **TC-01** |
| **FR-03** | **Result Visualization** | `Streamlit UI` (`src/ui/app.py`) | *Manual UI Test* |
| **FR-04** | **SQL Explanation** | `Streamlit UI` | *Manual UI Test* |
| **FR-05** | **Error Handling** | `LangGraph Orchestrator` (Retry Loop) | **TC-01** (Implicit) |
| **FR-06** | **Data Governance** | `DataGovernanceService` | **TC-03**, **TC-04**, **TC-05** |
| **FR-07** | **Schema Awareness** | `SchemaGraphService`, `SemanticGraph` | **TC-02** |
| **FR-08** | **Graph Generation** | `generate_graph_for_db.py`, `DBProfilingService` | **TC-06** |
| **FR-09** | **Database Agnostic** | `DBInterface`, `MySQLService` (Adapter) | *Code Review* |
| **FR-10** | **Self-Evolution** | `FeedbackService`, `GraphEvolutionService` | **TC-07** (Planned) |

## Conclusion
The Traceability Matrix demonstrates that every core requirement has been implemented in a specific component and validated by at least one automated or manual test case, ensuring a complete and verified system.
