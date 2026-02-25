import os
import requests  # type: ignore
from typing import Dict, Any, Optional

class GitHubClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def get_pr_diff(self, rep_full_name: str, pr_number: int) -> str:
        """
        Fetches the raw diff of the pull request to analyze code changes.
        """
        url = f"https://api.github.com/repos/{rep_full_name}/pulls/{pr_number}"
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"  # Get diff format
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch PR diff: {response.text}")
            return ""

    def get_repo_structure(self, repo_full_name: str, branch: str = "main") -> str:
        """
        Fetches the repository file tree up to 2 levels deep to understand context.
        """
        url = f"https://api.github.com/repos/{repo_full_name}/git/trees/{branch}?recursive=1"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            tree = response.json().get("tree", [])
            # Filter and truncate for prompt size
            files = [str(item["path"]) for item in tree if item["type"] == "blob"]
            return "\n".join(files[:100])  # type: ignore
        return "Unknown Structure"

    def get_file_content(self, repo_full_name: str, file_path: str, branch: str = "main") -> Optional[str]:
        """
        Fetches the content of a specific important file (e.g. package.json, requirements.txt, pom.xml).
        """
        url = f"https://raw.githubusercontent.com/{repo_full_name}/{branch}/{file_path}"
        headers = {"Authorization": f"token {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
             return response.text
        return None

    def post_comment(self, repo_full_name: str, issue_number: int, body: str) -> bool:
        """
        Posts a comment back to the GitHub PR (which is technically an issue comment).
        """
        url = f"https://api.github.com/repos/{repo_full_name}/issues/{issue_number}/comments"
        payload = {"body": body}
        response = requests.post(url, headers=self.headers, json=payload)
        return response.status_code == 201
