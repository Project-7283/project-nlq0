# 1. Introduction & Problem Definition

## 1.1 Purpose
The purpose of this document is to provide a comprehensive overview of the **Natural Language Query (NLQ) to SQL System**. It serves as the final project submission, detailing the system's architecture, design, implementation, and validation. This document is intended for project evaluators, technical stakeholders, and future developers who may maintain or extend the system.

## 1.2 Project Scope
The **NLQ-to-SQL System** is an intelligent interface that allows non-technical users to query relational databases using plain English.

### In-Scope
- **Natural Language Processing**: Converting free-text user questions into structured SQL queries.
- **SQL Execution**: Safely executing generated queries against a MySQL database.
- **Data Visualization**: Presenting query results in tabular format via a web interface.
- **Data Governance**: Enforcing security policies to prevent unauthorized access to sensitive data (PII).
- **Context Awareness**: Using vector embeddings and semantic graphs to understand database schema and relationships.
- **Multi-Model Support**: Orchestrating queries across different LLM providers (Gemini, OpenAI, Ollama).
- **Database Agnostic Design**: While MySQL is used as the reference implementation, the architecture uses an **Adapter Pattern** to support any RDBMS (PostgreSQL, Oracle, SQL Server) in the future.
- **Self-Evolution**: The system implements a reinforcement learning loop that uses user feedback to autonomously optimize the semantic graph (adjusting edge weights and creating virtual nodes) for improved future accuracy.

### Out-of-Scope
- **Data Modification**: The system is strictly **read-only** (SELECT statements only). INSERT, UPDATE, and DELETE operations are blocked.
- **User Authentication & Management**: To prioritize the robustness of the core NLQ engine and semantic graph architecture, multi-tenant authentication (OAuth/RBAC) was explicitly excluded from this phase. The system currently operates in a single-user mode suitable for internal tool deployment.
- **Complex Analytics**: Advanced statistical modeling or machine learning on the result set is not performed.

## 1.3 Problem Statement
In many organizations, valuable data is locked inside relational databases. Business users (analysts, managers, executives) often lack the SQL expertise required to extract this data. This creates a bottleneck where:
1.  **Dependency**: Business users must rely on technical teams for every data request.
2.  **Latency**: Simple questions can take days to answer due to backlog.
3.  **Inefficiency**: Data engineers spend time writing trivial queries instead of focusing on complex infrastructure tasks.

**The "Pain Point"**: The gap between *human language* (how users think) and *Structured Query Language* (how databases speak) hinders data-driven decision-making.

## 1.4 Proposed Solution
We propose an **AI-Powered NLQ Agent** that acts as a translator between the user and the database.

**High-Level Approach**:
1.  **Semantic Understanding**: The system maps the user's intent to specific database tables and columns using a **Semantic Graph**.
2.  **Context Retrieval**: It uses **Vector Search (RAG)** to find relevant schema information, reducing the context window needed for the LLM.
3.  **Governed Generation**: A Large Language Model (LLM) generates SQL, which is then validated against strict **Data Governance** policies to ensure security.
4.  **Self-Correction**: If the generated SQL fails, the system uses a **Retry Loop** to analyze the error and correct the query automatically.
5.  **Extensible Architecture**: The system is built with a modular design, allowing new database adapters to be plugged in without modifying the core logic.
6.  **Continuous Learning**: A feedback-driven evolution engine refines the semantic graph over time, ensuring the system gets smarter with every interaction.

This solution democratizes data access, allowing users to ask "Show me total sales by region" and receive immediate, accurate results.
