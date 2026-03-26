import os
import google.generativeai as genai  # type: ignore
from typing import Tuple

class AIEngine:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def layer_1_enhance_prompt(self, basic_prompt: str, repo_structure: str, key_files_context: str, pr_diff: str) -> str:
        """
        Layer 1: The Context-Aware Interceptor.
        Takes the user's basic prompt and massive repository context to generate a highly
        structured, restrictive, and comprehensive code review prompt.
        """
        system_instruction = f"""
        You are 'DULA Layer 1' - an expert prompt synthesis engine for codebase analysis.
        Your goal is to take a user's basic request and expand it into a magnificent, deeply technical, 
        and rigorous prompt for a downstream structural Code Review LLM.
        
        You will output exactly the instruction set for Layer 2. Ensure it strictly adopts the following Master Prompt format:

        You are an Expert Staff Engineer, Security Auditor, and strict Technical Interviewer reviewing a codebase.
        
        ## 🏗️ PROJECT CONTEXT
        - **Tech Stack & Versions:** (Extract this dynamically from the Key Core Files provided below)
        - **Project Structure:**
        {repo_structure}
        - **User's Request:** "{basic_prompt}"
        
        ## 🎯 FOCUS AREAS
        Based on the user's request, instruct the downstream LLM to execute a ruthless analysis of this project focusing on the categories mentioned by the user (or all if none specified): Security, Performance, Code Quality, Architecture, Bugs, Testing, DevOps.
        
        ## 🔍 ANALYSIS CRITERIA
        Depending on the selected focus areas, evaluate the codebase against these specific standards:
        - **Security:** Identify SQL/NoSQL Injection, XSS, broken Auth/Authz, CSRF, sensitive data exposure, and REST/GraphQL API security gaps.
        - **Performance:** Flag memory leaks, unnecessary frontend re-renders, N+1 query problems, blocking sync operations, and inefficient loops.
        - **Code Quality:** Critique naming conventions, identify duplicate code (DRY violations), flag massive functions missing Single Responsibility Principle (SRP), and evaluate overall maintainability.
        - **Architecture:** Review folder structure patterns, separation of concerns, scalability bottlenecks, and domain layer violations.
        - **Bugs:** Spot unhandled edge cases, null/undefined risks, async/await race conditions, and unsafe type coercions.
        - **Testing:** Identify zero-coverage critical paths, unit vs. integration gaps, and poor mock implementations.
        - **DevOps:** Spot hardcoded secrets, mismanaged environment variables, lacked Docker/build optimization, and missing telemetry/logging logic.
        
        REQUIREMENTS FOR Downstream LLM (Layer 2) in your Prompt:
        It MUST instruct the LLM to use a softer, professional tone (e.g. use terms like 'Observation' and 'Recommendation' instead of 'Flaw' or 'Wrong').
        It MUST instruct the LLM to format every finding strictly wrapped in GitHub Markdown `<details>` and `<summary>` tags for a collapsible UI.
        It MUST instruct the LLM to include '⏱ Estimated Fix Time', '⚠ Real-world Impact', and a visual 'Confidence Meter (e.g. ████████ 90%)'.
        It MUST instruct the LLM to summarize findings into an Action Plan: 🔥 Fix First, ⚡ Improve Next, 📦 Refactor Later.
        
        ---
        Here is the Context for your evaluation to inject securely into the prompt:
        Key Core Files (Dependencies/Config):
        {key_files_context}
        
        Current Code Changes (PR Diff):
        {pr_diff}
        ---

        Your output should JUST be the enhanced prompt text, written in the second person ("You are an Expert Staff Engineer...").
        Do not include pleasantries. Make it look as academic, rigorous, and specific to the codebase as possible.
        """

        try:
             response = self.model.generate_content(system_instruction)
             return response.text
        except Exception as e:
             import traceback
             traceback.print_exc()
             print(f"Error in Layer 1: {e}")
             return f"Error: Could not enhance prompt based on '{basic_prompt}'. Please check API keys."

    def layer_2_generate_review(self, confirmed_prompt: str, pr_diff: str) -> str:
        """
        Layer 2: The Executor.
        Takes the rigidly structured confirmed prompt and applies it to the PR Diff.
        """
        
        execution_prompt = f"""
        {confirmed_prompt}
        
        ---
        PULL REQUEST CODE DIFF TO REVIEW:
        {pr_diff}
        ---
        
        EXECUTION PARAMETERS:
        1. Format your output EXACTLY as the following technical Markdown template. Do not deviate.
        2. NEVER use chatty, conversational filler. Act completely like an automated Staff Engineer producing a strict Code Review.
        
        REQUIRED OUTPUT FORMAT (Do NOT provide generic advice. Be highly specific to the provided Tech Stack and Versions):

        # 🧠 Code Review Summary
        
        (Generate a professional Markdown Table summarizing the numerical count of issues found, grouped by Category and Severity)

        ```mermaid
        pie title Issues by Category
        "[Category 1]" : [Count]
        "[Category 2]" : [Count]
        ```

        ## Detailed Findings
        (Provide findings grouped exactly by their category. Every finding MUST be collapsible using `<details>` and `<summary>` tags.)

        ### [Category Name] (e.g. 🛡 Security, ⚡ Performance, 🧹 Code Quality)

        <details>
        <summary>🔴 Finding: [Specific Issue Name]</summary>
        
        *   **File:** `[FilePathFromDiff]` (Lines `[Start]-[End]`)
        *   **⏱ Estimated Fix Time:** [e.g. 5 mins]
        *   **Confidence:** [e.g. ████████ 90%]
        
        **🔍 Observation:** 
        [Explain what the code is currently doing without being overly judgmental.]
        
        **⚠ Real-world Impact:** 
        [Explain why this matters in production or architecture.]
        
        **💡 Recommendation:** 
        [Explain the fix softly and suggestively.]
        
        **Current Code:**
        ```
        (Exact snippet from PR diff)
        ```
        **Refactored Code:**
        ```
        (Actionable code correcting the issue)
        ```
        </details>
        
        ---
        (Repeat `<details>` blocks for other findings...)

        ## 🎯 Action Plan
        (Summarize the findings by Severity and Effort)
        
        - 🔥 **Fix First (High Impact, Low Effort)**
          - [Issue title and quick link to finding]
        - ⚡ **Improve Next (Medium Impact)**
          - [Issue title and quick link to finding]
        - 📦 **Refactor Later (Low Priority)**
          - [Issue title and quick link to finding]
        ---
        """

        try:
            response = self.model.generate_content(execution_prompt)
            return response.text
        except Exception as e:
             print(f"Error in Layer 2: {e}")
             return f"Error: Could not generate review. {e}"
