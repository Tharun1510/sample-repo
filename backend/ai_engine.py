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
        and rigorous prompt for a downstream structural LLM.
        
        Repository Structure Outline:
        {repo_structure}
        
        Key Core Files (Dependencies/Config):
        {key_files_context}
        
        Current Code Changes (PR Diff):
        {pr_diff}
        
        User's Basic Prompt: "{basic_prompt}"
        
        TASK:
        Generate a highly detailed "Enhanced Code Review Prompt". The prompt you generate should explicitly instruct 
        the downstream LLM to analyze the given PR Diff for:
        1. Time and Space Complexity
        2. Security vulnerabilities specific to the tech stack (inferred from the dependencies/context)
        3. Maintainability and readability
        4. Alignment with the overall repository architecture.
        
        CRITICAL RULES FOR THE ENHANCED PROMPT:
        - It MUST instruct the downstream LLM to act as a strict static analysis CLI tool, NOT a conversational AI.
        - It MUST instruct the LLM to provide EXACT LINE NUMBERS for every issue identified from the PR Diff.
        - It MUST instruct the LLM to provide concrete code snippets of the flaw alongside the suggested structural replacement.
        - It MUST instruct the LLM to assign an "Impact Severity" (Critical, High, Medium, Low) and a "Confidence Score" to each finding.
        - It MUST instruct the LLM to format the output in a highly structured Markdown report (e.g., using tables for metrics and defined technical sections for issues).
        
        Your output should JUST be the enhanced prompt text, written in the second person ("You are an expert...").
        Do not include pleasantries. Make it look as academic and rigorous as possible.
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
        1. Format your output as a highly technical Markdown report.
        2. NEVER use chatty, conversational filler (e.g., "Here is the review", "I found missing things").
        3. Act completely like an automated Code Analysis system producing a structured STDOUT log.
        4. For EVERY issue detected, reference the exact line of code from the PR payload.
        5. For EVERY issue, provide the flawed code block and the requested corrected code block (Suggestion).
        6. Start with a "Summary Metric Table" displaying overall Code Health and Security Posture.
        """

        try:
            response = self.model.generate_content(execution_prompt)
            return response.text
        except Exception as e:
             print(f"Error in Layer 2: {e}")
             return f"Error: Could not generate review. {e}"
