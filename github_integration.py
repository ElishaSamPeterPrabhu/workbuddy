"""
GitHub integration module for WorkBuddy (Jarvis Assistant).

Handles authentication, polling, and notifications for assigned issues, PRs, and reviews.

TODO: Move this module to /integrations/github.py as per modular structure.
"""
import requests
import json
import os
import datetime
from collections import defaultdict


class GitHubIntegration:
    def __init__(self):
        self.api_key = os.environ.get("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.user = None
        self.repos = []
        self.notifications = []

        # Initialize GitHub connection
        if self.api_key:
            self.init_connection()

    def init_connection(self):
        """Initialize connection to GitHub API and load basic user info"""
        try:
            # Get user info
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            if response.status_code == 200:
                self.user = response.json()
                return True
            else:
                print(f"GitHub API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"GitHub connection error: {str(e)}")
            return False

    def is_configured(self):
        """Check if GitHub integration is configured with a valid token"""
        return self.api_key and self.user is not None

    def get_user_info(self):
        """Get basic user information"""
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

    def get_notifications(self, all=False):
        """Get GitHub notifications"""
        if not self.is_configured():
            return {"error": "GitHub integration not configured"}

        try:
            params = {"all": "true"} if all else {}
            response = requests.get(
                f"{self.base_url}/notifications", headers=self.headers, params=params
            )

            if response.status_code == 200:
                self.notifications = response.json()

                # Format notifications for display
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
            else:
                print(f"GitHub API error: {response.status_code}")
                return {"error": f"GitHub API error: {response.status_code}"}
        except Exception as e:
            print(f"GitHub error: {str(e)}")
            return {"error": str(e)}

    def get_repos(self, limit=10):
        """Get user's repositories"""
        if not self.is_configured():
            return {"error": "GitHub integration not configured"}

        try:
            params = {"per_page": limit, "sort": "updated"}
            response = requests.get(
                f"{self.base_url}/user/repos", headers=self.headers, params=params
            )

            if response.status_code == 200:
                self.repos = response.json()

                # Format repos for display
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
            else:
                print(f"GitHub API error: {response.status_code}")
                return {"error": f"GitHub API error: {response.status_code}"}
        except Exception as e:
            print(f"GitHub error: {str(e)}")
            return {"error": str(e)}

    def get_recent_activity(self, limit=10):
        """Get recent activity from user's repositories"""
        if not self.is_configured():
            return {"error": "GitHub integration not configured"}

        if not self.repos:
            self.get_repos(limit=20)

        try:
            all_events = []

            # Get events for up to 5 repositories
            for repo in self.repos[:5]:
                repo_name = repo.get("full_name")
                response = requests.get(
                    f"{self.base_url}/repos/{repo_name}/events", headers=self.headers
                )

                if response.status_code == 200:
                    events = response.json()
                    all_events.extend(events)

            # Sort events by created_at
            all_events.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            # Format events for display
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

    def get_pull_requests(self, state="open"):
        """Get pull requests from user's repositories"""
        if not self.is_configured():
            return {"error": "GitHub integration not configured"}

        if not self.repos:
            self.get_repos(limit=20)

        try:
            all_prs = []

            # Get PRs for up to 5 repositories
            for repo in self.repos[:5]:
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

            # Format PRs for display
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

    def generate_summary(self):
        """Generate a human-readable summary of GitHub activity"""
        if not self.is_configured():
            return "GitHub integration is not configured. Please set up your GitHub token to enable this feature."

        try:
            # Get notifications
            notifications = self.get_notifications()
            if isinstance(notifications, dict) and "error" in notifications:
                notification_count = 0
            else:
                notification_count = len(notifications)

            # Get repositories
            repos = self.get_repos(limit=5)
            if isinstance(repos, dict) and "error" in repos:
                recent_repos = []
            else:
                recent_repos = repos

            # Get PRs
            prs = self.get_pull_requests()
            if isinstance(prs, dict) and "error" in prs:
                open_prs = []
            else:
                open_prs = prs

            # Build summary text
            summary = f"GitHub Summary for {self.user.get('login')}:\n\n"

            # Notifications
            summary += f"You have {notification_count} unread notifications.\n\n"

            # Recent repositories
            summary += "Recent repositories:\n"
            for repo in recent_repos[:3]:
                summary += f"- {repo.get('name')}: {repo.get('description') or 'No description'}\n"

            # Open PRs
            summary += f"\nYou have {len(open_prs)} open pull requests.\n"

            return summary

        except Exception as e:
            print(f"GitHub summary error: {str(e)}")
            return f"Error generating GitHub summary: {str(e)}"


if __name__ == "__main__":
    # Simple test script
    github = GitHubIntegration()

    if github.is_configured():
        print("GitHub integration is configured.")
        user_info = github.get_user_info()
        print(
            f"Logged in as: {user_info.get('name', 'Unknown')} ({user_info.get('username', 'Unknown')})"
        )

        print("\nGenerating summary...")
        summary = github.generate_summary()
        print(summary)
    else:
        print("GitHub integration is not configured.")
        print("Please set the GITHUB_TOKEN environment variable to use this feature.")
