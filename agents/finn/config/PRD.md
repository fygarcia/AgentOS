This is the definitive **Product Requirements Document (PRD)** for your project. I have structured it to clearly distinguish between the **Domain-Agnostic Agentic OS** (the engine) and **Agent Finn** (the financial specialist).


# ---

**PRD.md: Project "Omni-Finn"**

## **1\. Executive Summary**

**Omni-Finn** is a state-of-the-art, local-first autonomous multi-agent system designed to bridge the gap between messy financial data and high-level investment strategy. It operates on a high-performance homelab (RTX 4090\) and uses a 3-layer architecture to ensure that financial calculations remain **deterministic** while analysis remains **probabilistic** and insightful.

## ---

**2\. Core Architecture: The "Chassis" vs. "Passenger"**

This project maintains a strict separation of concerns to allow the underlying agentic framework to be reused for non-financial domains in the future.

### **2.1 The Agentic OS (The Domain-Agnostic Engine)**

* **Skill-Oriented Registry:** All system capabilities must be registered in SKILLS.md as independent, testable Python scripts.  
* **Dual-Model Orchestration:** \* **The Planner/Auditor:** High-reasoning model (e.g., DeepSeek-R1-32B+) that handles logic, error diagnosis, and verification.  
  * **The Actor:** Fast, tool-calling model (e.g., Qwen2.5-Coder-7B) that generates code and executes CLI commands.  
* **The Self-Healing (Annealing) Loop:** An autonomous recovery cycle where the Auditor identifies script failures, the Actor patches the code in a sandbox, and the system promotes the fix to production upon verification.

### **2.2 Agent Finn (The Financial Analyst)**

* **Role:** Financial Custodian and Portfolio Manager.  
* **Domain Intelligence:** Specialized in parsing bank statements, calculating yield-to-maturity (YTM), monitoring dividend schedules, and correlating macro-economic news with specific portfolio holdings.

## ---

**3\. Core Features & Functional Requirements**

### **3.1 Data Integrity & Ingestion (The Accountant)**

* **Deterministic Normalization:** All raw inputs (PDF/CSV/XLS) must be converted to a standard JSON schema before database entry.  
* **Reconciliation Engine:** Automated cross-referencing between "Expected Cash Flow" (from bond maturity/dividend dates) and "Actual Cash Flow" (from bank statements).  
* **Zero-Float Math:** All financial calculations must use the Python decimal library to prevent rounding errors.

### **3.2 Relentless Research (The Analyst)**

* **Delta-Only Reporting:** The system shall filter general market noise to provide "Delta Reports"—summaries explaining exactly how a news event shifts the risk/reward profile of a *specific* current holding.  
* **Vectorized Memory:** Use LanceDB to store historical SEC filings, news, and past decisions for long-term "Semantic Memory."

### **3.3 The "Active" Self-Healing Loop**

* **Requirement:** If a bank changes its PDF layout, the agent must:  
  1. Detect the parse error.  
  2. Propose a new regex or parsing logic.  
  3. Test the logic against the failed file.  
  4. Update the SOP\_daily\_ingest.md directive to reflect the change.

## ---

**4\. Technical Stack (2026 Homelab Edition)**

| Component | Technology | Rationale |
| :---- | :---- | :---- |
| **GPU/Host** | NVIDIA RTX 4090 (24GB VRAM) | Local inference of 30B+ reasoning models. |
| **Inference Server** | Ollama / vLLM | Local API hosting with OpenAI-compatible endpoints. |
| **Orchestration** | LangGraph | Handles cyclical, stateful agent workflows. |
| **Persistence** | SQLite (Relational) \+ LanceDB (Vector) | SQL for holdings; Vector for research. |
| **Models** | DeepSeek-R1 (Planner), Qwen2.5-Coder (Executor) | Best-in-class local reasoning and tool-calling. |

## ---

**5\. Scope & Constraints (Non-Goals)**

* **No Autonomous Trading:** For safety, the agent can recommend trades and generate "Order Drafts," but it cannot execute buys/sells on an exchange.  
* **Local-First Privacy:** No financial data should ever leave the local network unless explicitly sent to a user-defined cloud deliverable (e.g., Google Sheets).  
* **Model Agnostic:** The system must be able to swap Local LLM for Cloud LLM (Gemini/Claude) via a single .env toggle.

## ---

**6\. Project Roadmap**

### **Phase 1: The Foundation (Current)**

* Establish AGENTS.md, SKILLS.md, and SELF\_HEALING.md.  
* Initialize the SQLite portfolio.db schema.  
* Build the basic Execution/ scripts for database CRUD operations.

### **Phase 2: The Ingestion Engine**

* Implement the OCR Specialist for PDF parsing.  
* Connect the "Actor-Auditor" loop to ensure data entered into the DB is 100% accurate.

### **Phase 3: The Analyst & Research Loop**

* Implement web-research skills.  
* Develop the "Delta Report" logic using the reasoning model.

### ---

