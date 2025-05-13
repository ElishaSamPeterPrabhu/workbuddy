"""
Manages interactive, multi-round file search sessions for WorkBuddy.
"""

from typing import List, Optional, Dict, Any
from core.filesearch import run_shell_command
import os
import platform
import fnmatch


def run_file_search(pattern: str, directory: Optional[str] = None) -> List[str]:
    if directory and directory.lower() == "desktop":
        abs_directory = os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        abs_directory = os.path.abspath(directory or ".")

    print(f"Searching in directory: {abs_directory}")
    print(f"Pattern: {pattern}")

    try:
        # Non-recursive search for all patterns if a specific directory is mentioned
        if pattern == "*":
            print("Pattern is '*', using non-recursive file listing.")
            files = [
                os.path.abspath(os.path.join(abs_directory, f))
                for f in os.listdir(abs_directory)
                if os.path.isfile(os.path.join(abs_directory, f))
            ]
            print(f"Non-recursive file listing found {len(files)} files.")
            return files
        else:
            if platform.system() == "Windows":
                command = f'dir "{pattern}" /a-d /b'
                result = run_shell_command(command, cwd=abs_directory)
                print(f"Shell command return code: {result['returncode']}")
                print(f"Shell command stdout:\n{result['stdout']}")
                print(f"Shell command stderr:\n{result['stderr']}")
                if result["returncode"] == 0 and result["stdout"]:
                    found = [
                        os.path.abspath(os.path.join(abs_directory, line))
                        for line in result["stdout"].splitlines()
                        if line.strip()
                    ]
                    print(f"Shell search found {len(found)} files.")
                    for f in found:
                        print(f"Found: {f}")
                    return found
                else:
                    print("Shell search found nothing. Falling back to Python search…")
            # Fallback: Python non-recursive pattern match
            try:
                files = [
                    os.path.abspath(os.path.join(abs_directory, f))
                    for f in os.listdir(abs_directory)
                    if os.path.isfile(os.path.join(abs_directory, f))
                    and fnmatch.fnmatch(f, pattern)
                ]
                print(f"Python search found {len(files)} files.")
                return files
            except PermissionError as e:
                print(
                    f"[WARNING] Permission denied when listing files in {abs_directory}: {e}"
                )
                return []
    except PermissionError as e:
        print(
            f"[WARNING] Permission denied when accessing directory {abs_directory}: {e}"
        )
        return []


class FileSearchSession:
    """
    Handles state and logic for an interactive, AI-driven file search session.
    """

    def __init__(self, user_query: str) -> None:
        """
        Initialize a new file search session.
        """
        self.user_query = user_query
        self.round = 0
        self.max_rounds = 10
        self.last_results: List[str] = []
        self.history: List[Dict[str, Any]] = []

    def run_search_round(
        self, pattern: str, directory: Optional[str] = None
    ) -> List[str]:
        """
        Run a file search and update session state.
        """
        self.round += 1
        results = run_file_search(pattern, directory)
        self.last_results = results
        self.history.append(
            {
                "round": self.round,
                "pattern": pattern,
                "directory": directory,
                "results": results,
            }
        )
        return results

    def should_continue(self) -> bool:
        """
        Determine if the session should continue.
        """
        return self.round < self.max_rounds

    def get_last_results(self) -> List[str]:
        """
        Get the results from the last search round.
        """
        return self.last_results

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the full search history.
        """
        return self.history
