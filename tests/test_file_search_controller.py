"""
Tests for the AI-driven file search controller in WorkBuddy.
"""

import pytest
from typing import List, Dict, Any
from core.file_search_controller import ai_file_search_loop
from core.file_search_session import FileSearchSession


class MockAIClient:
    """
    Mock AIClient for testing file search loop.
    Returns a fixed sequence of commands, then a stop.
    """

    def __init__(self, commands: List[Dict[str, Any]]):
        self.commands = commands
        self.call_count = 0

    def get_file_search_command(self, context: dict) -> dict:
        if self.call_count < len(self.commands):
            cmd = self.commands[self.call_count]
            self.call_count += 1
            return cmd
        return {"action": "stop", "ai_response": "Done."}


def test_ai_file_search_loop_runs_multiple_rounds(tmp_path):
    """
    Test that ai_file_search_loop runs the correct number of rounds and returns expected results.
    """
    # Patch run_file_search to return predictable results
    import core.file_search_session as fss

    def fake_run_file_search(pattern: str, directory: str = None) -> List[str]:
        return [f"{directory or '.'}/{pattern}"]

    fss.run_file_search = fake_run_file_search

    # Prepare mock AI commands: 2 rounds, then stop
    commands = [
        {"action": "file_search", "pattern": "*.py", "directory": "src"},
        {"action": "file_search", "pattern": "test_*.py", "directory": "tests"},
        {"action": "stop", "ai_response": "Done."},
    ]
    ai_client = MockAIClient(commands)
    user_query = "Find all Python files."
    results = ai_file_search_loop(user_query, ai_client)
    # Should run 2 rounds, so last results should match the last file search
    assert results == ["tests/test_*.py"]
    assert ai_client.call_count == 3
