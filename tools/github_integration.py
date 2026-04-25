"""
GitHub Integration
=================
Connect to GitHub for repo operations.

Features:
- Clone/push repos
- Create issues/PRs
- Create gists
- View activity
"""

import os
import requests
from typing import Optional, Dict, List
from pathlib import Path


class GitHubClient:
    """GitHub API client."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def is_configured(self) -> bool:
        """Check if GitHub is configured."""
        return bool(self.token)
    
    def get_user(self) -> Optional[Dict]:
        """Get current user."""
        if not self.is_configured():
            return None
        response = requests.get(
            f"{self.base_url}/user",
            headers=self.headers
        )
        return response.json() if response.status_code == 200 else None
    
    def list_repos(self) -> List[Dict]:
        """List user repositories."""
        if not self.is_configured():
            return []
        response = requests.get(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                params={"per_page": 100}
            )
        return response.json() if response.status_code == 200 else []
    
    def create_repo(
        self,
        name: str,
        private: bool = False,
        description: str = ""
    ) -> Optional[Dict]:
        """Create a new repository."""
        if not self.is_configured():
            return None
        
        data = {
            "name": name,
            "private": private,
            "description": description,
            "auto_init": True
        }
        response = requests.post(
            f"{self.base_url}/user/repos",
            json=data,
            headers=self.headers
        )
        return response.json() if response.status_code == 201 else None
    
    def get_repo(self, owner: str, repo: str) -> Optional[Dict]:
        """Get repository info."""
        response = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}",
            headers=self.headers
        )
        return response.json() if response.status_code == 200 else None
    
    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str = ""
    ) -> Optional[Dict]:
        """Create an issue."""
        if not self.is_configured():
            return None
        
        data = {"title": title, "body": body}
        response = requests.post(
            f"{self.base_url}/repos/{owner}/{repo}/issues",
            json=data,
            headers=self.headers
        )
        return response.json() if response.status_code == 201 else None
    
    def list_issues(self, owner: str, repo: str) -> List[Dict]:
        """List issues."""
        response = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}/issues",
            headers=self.headers
        )
        return response.json() if response.status_code == 200 else []
    
    def create_gist(
        self,
        description: str,
        files: Dict[str, str],
        public: bool = False
    ) -> Optional[Dict]:
        """Create a gist."""
        if not self.is_configured():
            return None
        
        data = {
            "description": description,
            "public": public,
            "files": files
        }
        response = requests.post(
            f"{self.base_url}/gists",
            json=data,
            headers=self.headers
        )
        return response.json() if response.status_code == 201 else None


def clone_repo(url: str, path: str = ".") -> str:
    """Clone a GitHub repository."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "clone", url, path],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"


def push_to_github(message: str = "Update") -> str:
    """Commit and push changes."""
    import subprocess
    try:
        subprocess.run(["git", "add", "-A"], capture_output=True)
        subprocess.run(["git", "commit", "-m", message], capture_output=True)
        result = subprocess.run(
            ["git", "push"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    print("=" * 50)
    print("GitHub Integration")
    print("=" * 50)
    
    # Check if configured
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print("[OK] GITHUB_TOKEN set")
        client = GitHubClient(token)
        user = client.get_user()
        if user:
            print(f"   Logged in as: {user.get('login')}")
        else:
            print("   [ERROR] Invalid token")
    else:
        print("[INFO] GITHUB_TOKEN not set")
        print("")
        print("To connect to GitHub:")
        print("1. Go to https://github.com/settings/tokens")
        print("2. Create a Personal Access Token (repo scope)")
        print("3. Set environment variable:")
        print("   Windows: setx GITHUB_TOKEN your_token_here")
        print("   Or add to .env file in project")
    
    print("")
    print("Git operations available:")
    print("  git remote add origin <url>")
    print("  git push -u origin main")