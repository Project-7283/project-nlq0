# Final Project Documentation: NLQ-to-SQL System

This directory contains the complete documentation for the Natural Language Query to SQL System final project.

## Table of Contents

1.  [**Introduction & Problem Definition**](01_introduction_problem_definition.md)
    *   Purpose, Scope, Problem Statement, Proposed Solution.
2.  [**Requirements Specification**](02_requirements_specification.md)
    *   User Personas, Functional/Non-Functional Requirements, Use Case Diagram.
3.  [**System Architecture & Design**](03_system_architecture_design.md)
    *   Architecture, Tech Stack, DB Schema, Component & Sequence Diagrams.
4.  [**Implementation & Technical Details**](04_implementation_technical_details.md)
    *   Setup, Algorithms, API Docs, Integrations.
5.  [**Testing & Quality Assurance**](05_testing_quality_assurance.md)
    *   Test Plan, Test Cases, Bug Reports.
6.  [**User Manual & Maintenance**](06_user_manual_maintenance.md)
    *   Installation, User Guide, Future Enhancements.
7.  [**Traceability Matrix**](07_traceability_matrix.md)
    *   Mapping Requirements to Components and Tests.

---
*Generated on December 22, 2025*

## Quick Start

To run the application:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup Database & Data
./init/setup_data.sh

# 3. Generate Semantic Graph
python init/generate_graph_for_db.py

# 4. Run Application
streamlit run src/main.py
```
