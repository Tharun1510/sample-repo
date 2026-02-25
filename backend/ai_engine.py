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
        
        Please format your output beautifully in Markdown. Use headings, bullet points, and code blocks
        where appropriate to highlight specific lines in the diff.
        """

        try:
            response = self.model.generate_content(execution_prompt)
            return response.text
        except Exception as e:
             print(f"Error in Layer 2: {e}")
             return f"Error: Could not generate review. {e}"
