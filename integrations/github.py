"""
GitHub integration module for WorkBuddy (Jarvis Assistant).

Handles authentication, polling, and data access for assigned issues, PRs, and reviews.
"""

import requests
import os
import datetime
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv

load_dotenv()


class GitHubIntegration:
    """Integration class for interacting with the GitHub API."""

    def __init__(self) -> None:
        """Initialize the GitHubIntegration with environment token and headers."""
        self.api_key: str = os.environ.get("GITHUB_TOKEN", "")
        self.base_url: str = "https://api.github.com"
        self.headers: Dict[str, str] = {
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.user: Optional[Dict[str, Any]] = None
        self.repos: List[Dict[str, Any]] = []
        self.notifications: List[Dict[str, Any]] = []
        if self.api_key:
            self.init_connection()

    def init_connection(self) -> bool:
        """Initialize connection to GitHub API and load basic user info."""
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            if response.status_code == 200:
                self.user = response.json()
                return True
            return False
        except Exception as e:
            print(f"GitHub connection error: {str(e)}")
            return False

    def is_configured(self) -> bool:
        """Check if GitHub integration is configured with a valid token."""
        return bool(self.api_key and self.user is not None)

    def get_user_info(self) -> Union[Dict[str, Any], Dict[str, str]]:
        """Get basic user information from GitHub."""
        if not self.is_configured():
            return {"error": "GitHub integration not configured"}
        return {
            "username": self.user.get("login"),
            "name": self.user.get("name"),
            "avatar_url": self.user.get("avatar_url"),
            "public_repos": self.user.get("public_repos"),
            "followers": self.user.get("followers"),
            "following": self.user.get("following"),
        }

    def get_notifications(
        self, all: bool = False
    ) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """Get GitHub notifications for the authenticated user."""
        if not self.is_configured():
            return {"error": "GitHub integration not configured"}
        try:
            params = {"all": "true"} if all else {}
            response = requests.get(
                f"{self.base_url}/notifications", headers=self.headers, params=params
            )
            if response.status_code == 200:
                self.notifications = response.json()
                formatted = []
                for notification in self.notifications:
                    formatted.append(
                        {
                            "id": notification.get("id"),
                            "repository": notification.get("repository", {}).get(
                                "name"
                            ),
                            "subject": notification.get("subject", {}).get("title"),
                            "type": notification.get("subject", {}).get("type"),
                            "reason": notification.get("reason"),
                            "updated_at": notification.get("updated_at"),
                        }
                    )
                return formatted
            return {"error": f"GitHub API error: {response.status_code}"}
        except Exception as e:
            print(f"GitHub error: {str(e)}")
            return {"error": str(e)}

    def get_repos(self, limit: int = 10) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """Get user's repositories from GitHub."""
        if not self.is_configured():
            return {"error": "GitHub integration not configured"}
        try:
            params = {"per_page": limit, "sort": "updated"}
            response = requests.get(
                f"{self.base_url}/user/repos", headers=self.headers, params=params
            )
            if response.status_code == 200:
                self.repos = response.json()
                formatted = []
                for repo in self.repos:
                    formatted.append(
                        {
                            "id": repo.get("id"),
                            "name": repo.get("name"),
                            "full_name": repo.get("full_name"),
                            "description": repo.get("description"),
                            "language": repo.get("language"),
                            "stars": repo.get("stargazers_count"),
                            "forks": repo.get("forks_count"),
                            "updated_at": repo.get("updated_at"),
                            "url": repo.get("html_url"),
                        }
                    )
                return formatted
            return {"error": f"GitHub API error: {response.status_code}"}
        except Exception as e:
            print(f"GitHub error: {str(e)}")
            return {"error": str(e)}

    def get_recent_activity(
        self, limit: int = 10
    ) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """Get recent activity from user's repositories."""
        if not self.is_configured():
            return {"error": "GitHub integration not configured"}
        if not self.repos:
            self.get_repos(limit=20)
        try:
            all_events = []
            for repo in self.repos[:5]:
                repo_name = repo.get("full_name")
                response = requests.get(
                    f"{self.base_url}/repos/{repo_name}/events", headers=self.headers
                )
                if response.status_code == 200:
                    events = response.json()
                    all_events.extend(events)
            all_events.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            formatted = []
            for event in all_events[:limit]:
                event_type = event.get("type", "").replace("Event", "")
                actor = event.get("actor", {}).get("login")
                repo = event.get("repo", {}).get("name")
                created_at = event.get("created_at")
                formatted.append(
                    {
                        "type": event_type,
                        "actor": actor,
                        "repo": repo,
                        "created_at": created_at,
                    }
                )
            return formatted
        except Exception as e:
            print(f"GitHub error: {str(e)}")
            return {"error": str(e)}

    def get_pull_requests(
        self, state: str = "open"
    ) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """Get pull requests from all user's repositories."""
        if not self.is_configured():
            return {"error": "GitHub integration not configured"}
        if not self.repos:
            self.get_repos(limit=100)  # Fetch more repos if possible
        try:
            all_prs = []
            for repo in self.repos:
                repo_name = repo.get("full_name")
                response = requests.get(
                    f"{self.base_url}/repos/{repo_name}/pulls",
                    headers=self.headers,
                    params={"state": state},
                )
                if response.status_code == 200:
                    prs = response.json()
                    for pr in prs:
                        pr["repo"] = repo_name
                    all_prs.extend(prs)
            formatted = []
            for pr in all_prs:
                formatted.append(
                    {
                        "number": pr.get("number"),
                        "title": pr.get("title"),
                        "state": pr.get("state"),
                        "user": pr.get("user", {}).get("login"),
                        "repo": pr.get("repo"),
                        "created_at": pr.get("created_at"),
                        "updated_at": pr.get("updated_at"),
                        "url": pr.get("html_url"),
                    }
                )
            return formatted
        except Exception as e:
            print(f"GitHub error: {str(e)}")
            return {"error": str(e)}

    def get_pull_requests_for_repo(
        self, repo_full_name: str, state: str = "open", user: Optional[str] = None
    ) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """Get pull requests for a specific repository by full name (e.g., 'trimble-oss/modus-wc-2.0').

        Args:
            repo_full_name (str): The full name of the repository (e.g., 'owner/repo').
            state (str, optional): The state of the pull requests to fetch. Defaults to "open".
            user (Optional[str], optional): Filter PRs by author, assignee, or requested reviewer. Defaults to None.

        Returns:
            Union[List[Dict[str, Any]], Dict[str, str]]: A list of pull requests or an error dict.
        """
        if not self.is_configured():
            return {"error": "GitHub integration not configured"}
        try:
            response = requests.get(
                f"{self.base_url}/repos/{repo_full_name}/pulls",
                headers=self.headers,
                params={"state": state},
            )
            if response.status_code == 200:
                prs = response.json()
                if user:
                    user_lc = user.lower()
                    prs = [
                        pr
                        for pr in prs
                        if pr.get("user", {}).get("login", "").lower() == user_lc
                        or any(
                            a.get("login", "").lower() == user_lc
                            for a in pr.get("assignees", [])
                        )
                        or any(
                            r.get("login", "").lower() == user_lc
                            for r in pr.get("requested_reviewers", [])
                        )
                    ]
                formatted = []
                for pr in prs:
                    formatted.append(
                        {
                            "number": pr.get("number"),
                            "title": pr.get("title"),
                            "state": pr.get("state"),
                            "user": pr.get("user", {}).get("login"),
                            "repo": repo_full_name,
                            "created_at": pr.get("created_at"),
                            "updated_at": pr.get("updated_at"),
                            "url": pr.get("html_url"),
                        }
                    )
                return formatted
            return {"error": f"GitHub API error: {response.status_code}"}
        except Exception as e:
            print(f"GitHub error: {str(e)}")
            return {"error": str(e)}

    def generate_summary(self) -> str:
        """Generate a human-readable summary of GitHub activity."""
        if not self.is_configured():
            return "GitHub integration is not configured. Please set up your GitHub token to enable this feature."
        try:
            notifications = self.get_notifications()
            notification_count = (
                0
                if isinstance(notifications, dict) and "error" in notifications
                else len(notifications)
            )
            repos = self.get_repos(limit=5)
            repo_count = (
                0 if isinstance(repos, dict) and "error" in repos else len(repos)
            )
            return f"GitHub Summary: {notification_count} notifications, {repo_count} repos."
        except Exception as e:
            return f"Error generating summary: {str(e)}"
