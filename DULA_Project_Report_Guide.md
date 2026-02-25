# DULA: Dual-Layer LLM Architecture for Automated Prompt Optimization and Code Review Enhancement
**Project Report Source Guide**

*Note to the Report Writer: This document contains all the technical details, architecture descriptions, buzzwords, and module overviews needed to formulate a 70+ page final-year technical report. You can expand on each section by adding standard college padding (SDLC methodologies like Agile/Waterfall, Feasibility Studies, UML diagrams, etc.).*

---

## 1. Abstract
Manual code review is a severe bottleneck in modern CI/CD pipelines. While Large Language Models (LLMs) offer automated review capabilities, they suffer from hallucination and lack of deep codebase context when deployed naively. To solve this, we present **DULA (Dual-Layer LLM Architecture)**. DULA operates as an Asynchronous Event-Driven GitHub application. Instead of relying on a single conversational LLM prompt, DULA implements a *Holistic Repository Context Parsing* engine (Layer 1) that maps project semantics and dependencies. Layer 1 synthesizes a highly restrictive, academically rigorous execution prompt which is then mathematically verified by a Human-in-the-Loop (HITL). Upon authorization, Layer 2 (The Executor) leverages this pre-computed semantic context to perform highly accurate, strict static-analysis equivalent code reviews directly within the GitHub Pull Request interface. To enhance UX, DULA also includes a custom Chromium-based Client UI extension for one-click native GitHub DOM injection.

## 2. Problem Statement
1. **Lack of Repository Context in LLMs:** Standard AI code reviewers only look at the PR Diff. They do not know what framework the project is using, what the dependency (`package.json`/`requirements.txt`) constraints are, or the directory structure. This causes them to suggest architecture-breaking code.
2. **Conversational Hallucination:** Normal LLMs output chatty, unstructured text. Enterprise software teams require strict, structured metric logging (e.g., SonarQube).
3. **Workflow Disruption:** Developers have to leave GitHub, go to an AI chat bot, paste code, and copy the results back.

## 3. Proposed Solution Architecture (The DULA Framework)
DULA solves these problems using a three-pronged architecture:

### A. The Client-Side Chromium Interceptor (UI Layer)
A native web extension that continuously monitors the GitHub Document Object Model (DOM). When a Pull Request is detected, it actively injects a Custom Trigger Node (`🧠 Request DULA Review`) into the GitHub interface. This bypasses the need for CLI commands and provides a seamless UI/UX. Clicking the button emits a JSON payload to the backend REST API.

### B. The Event-Driven FastAPI Orchestrator (Middleware)
A robust Python backend leveraging `FastAPI`, `Uvicorn`, and `Smee.io` (for Webhook tunneling). It exposes asynchronous endpoints (`/webhook`, `/trigger-review`) to consume events from both GitHub natively and the Chromium Extension. It enforces cryptographic payload validation to prevent unauthorized trigger events.

### C. The Dual-Layer LLM Cognitive Engine (Core AI)
The brain of the system, powered by the `google-generativeai` SDK (Gemini 1.5 Flash).
*   **Layer 1 (The Context Interceptor):** Reaches back into the GitHub API (`PyGithub`/`requests`) to recursively map the entire repository file tree. It extracts semantic configuration files. It then uses LLM reasoning to output a massive *Enhanced Prompt Schema*.
*   **Human-In-The-Loop (HITL) Validation:** The mathematical output of Layer 1 is posted to the PR. A human developer must authorize the operation via a `/confirm` command, preventing runaway AI errors.
*   **Layer 2 (The Execution Matrix):** Consumes the cryptographically bound original Pull Request Diff *and* the heavily restricted Layer 1 Schema. Layer 2 is explicitly programmed via static constraints to act as a CLI Static Analyzer, outputting exact line numbers, architectural impact severities, and replacement chunks in strict Markdown template format.

---

## 4. Hardware and Software Specifications
**(Expand these significantly for the report)**
*   **Backend:** Python 3.10+, FastAPI framework, Uvicorn ASGI server.
*   **Client Extension:** HTML5, CSS3, DOM Manipulation via vanilla JavaScript, Manifest V3.
*   **AI Infrastructure:** Google Gemini Pro/Flash API integration via `google.generativeai`.
*   **Version Control & Integration:** Git, GitHub API (Webhooks, Pull Requests, Comments), Personal Access Tokens (PAT).
*   **Development Tools:** VS Code, Git Bash.

---

## 5. Detailed Module Breakdown (For UML & Data Flow Diagrams)

### Module 1: `main.py` (The Routing Matrix)
This module acts as the traffic controller. 
*   **Endpoints:** `@app.post("/webhook")` and `@app.post("/trigger-review")`.
*   **Logic:** It parses incoming JSON payloads. If the `action` is `opened` or `created`, it parses the comment body.
*   **State Management:** It maintains a dictionary `pending_reviews = {}` holding the state of a PR between Layer 1 execution and Human Confirmation. This simulates a temporary Distributed Cache memory state.

### Module 2: `github_client.py` (The API Bridge)
Handles all external HTTP communications with GitHub's REST API.
*   `get_pr_diff()`: Fetches the raw `.diff` payload of the Pull Request.
*   `get_repo_structure()`: Uses the Git Trees API (`/git/trees/{branch}?recursive=1`) to pull the entire topological map of the repository, crucial for Layer 1 context.
*   `post_comment()`: Injects AI generated output back into the GitHub Issue Timeline.

### Module 3: `ai_engine.py` (The Dual-Layer Logic)
The core algorithmic component. 
*   **Layer 1 Prompt Construction:** Injects the basic user prompt, the `repo_structure`, and `key_files_context` into a massive structural prompt. It mathematically limits the output space of the LLM to just formal instructions.
*   **Layer 2 Template Enforcement:** It forces the AI to output exactly matching a strict Markdown template: `Summary`, `Findings Overview` (4 categories), and `Detailed Findings` (Line numbers, Flawed Snippet, Replacement Snippet, Severity, Confidence).

### Module 4: The Chromium Extension (`content.js`, `manifest.json`, `styles.css`)
*   **DOM Observer:** Uses `MutationObserver` to watch for Single-Page Application (SPA) DOM changes in GitHub's React framework.
*   **CORS Request:** Utilizes the Fetch API to send `POST` requests across origins (`github.com` to `localhost`/`Render`) to trigger the FastAPI backend.

---

## 6. How to Expand this to 70 Pages (Tips for the Writer)

1.  **Literature Review (10 Pages):** Write about the history of Code Review. Discuss manual code review vs. Static Analysis Tools (SonarQube) vs. LLMs. Discuss the limitations of ChatGPT for code review (hallucination, no repo context). Cite papers on "Prompt Engineering" and "Agentic Workflows".
2.  **System Analysis (10 Pages):** Include Feasibility Study, Functional Requirements, Non-Functional Requirements (Latency, Security, Extensibility).
3.  **System Design (15 Pages):** You must draw UML Diagrams:
    *   **Use Case Diagram:** Actors: Developer, Reviewer, GitHub System, DULA System.
    *   **Sequence Diagram:** Show the flow from Extension Click -> FastAPI -> GitHub API (fetch code) -> Gemini Layer 1 -> GitHub API (post confirm) -> User Confirm -> FastAPI -> Gemini Layer 2 -> GitHub API.
    *   **Architecture Diagram:** Show the Webhook tunneling architecture.
4.  **Implementation (15 Pages):** Paste code snippets from `main.py`, `ai_engine.py`, and `content.js`. Explain what each function does mathematically/logically. Explain FastAPI routing and REST concepts.
5.  **Software Testing (10 Pages):** Write out test cases. 
    *   *Test 1:* Webhook Validation failure (403 error handled).
    *   *Test 2:* Extension DOM Injection verification.
    *   *Test 3:* Layer 2 formatting template strictness.
6.  **Results & Conclusion (10 Pages):** Include screenshots of the Extension glowing button and the incredibly formatted Markdown tables outputted by the bot. Conclude that Dual-Layer Prompt Engineering significantly outperforms zero-shot LLM requests.
