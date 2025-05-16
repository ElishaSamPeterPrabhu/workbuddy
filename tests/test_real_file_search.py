"""
Interactive test script for file search functionality using Everything SDK.
This script allows testing natural language file search queries in an interactive shell.
"""

import os
from typing import Optional, Any

from core.ai_file_search_handler import file_search_handler
from core.everything_search import search_engine


def run_query(query: str) -> None:
    """
    Run a natural language file search query and display results.
    
    Args:
        query: Natural language query string
    """
    print(f"\nQuery: \"{query}\"")
    print("-" * 80)
    
    # Print debug info
    print(f"Everything SDK available: {search_engine.available}")
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    print(f"Desktop path: {desktop_path}")
    print(f"Desktop exists: {os.path.exists(desktop_path)}")
    
    # Run the search
    result = file_search_handler.natural_language_search(query)
    print(result)
    print("-" * 80)


def interactive_mode() -> None:
    """Run an interactive query loop for testing file search."""
    print("\n=== Interactive File Search ===\n")
    print("Enter a natural language query to search for files.")
    print("Examples:")
    print("  - check_colab.txt in Desktop")
    print("  - *.txt in Desktop")
    print("\nType 'exit' or 'quit' to end the session.")
    
    while True:
        query = input("\nEnter query: ").strip()
        if query.lower() in ('exit', 'quit', 'q'):
            break
        
        if query:
            run_query(query)


def main() -> None:
    """Main function to start the interactive file search test."""
    # Skip sample queries and go directly to interactive mode
    interactive_mode()


if __name__ == "__main__":
    main() 