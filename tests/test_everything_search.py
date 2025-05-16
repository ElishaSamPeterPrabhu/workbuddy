"""
Test script for the Everything SDK file search implementation.
This script demonstrates both direct file operations and natural language search.
"""

import os
import json
import argparse
from pathlib import Path

# Import the new file search handlers
from core.ai_file_search_handler import file_search_handler
from core.everything_search import search_engine

def test_direct_operations():
    """Test direct file/folder operations."""
    print("\n=== Testing Direct File Operations ===\n")
    
    # Test home directory operations
    home_dir = str(Path.home())
    print(f"Listing folders in {home_dir}:")
    result = file_search_handler.process_ai_command({"action": "list_folders", "directory": home_dir})
    folders = result.get("folders", [])
    print(f"Found {len(folders)} folders")
    for i, folder in enumerate(folders[:5], 1):
        print(f"{i}. {folder}")
    if len(folders) > 5:
        print(f"...and {len(folders) - 5} more folders")
    
    # Test desktop operations
    desktop = os.path.join(home_dir, "Desktop")
    if os.path.exists(desktop):
        print(f"\nListing files on Desktop:")
        result = file_search_handler.process_ai_command({"action": "list_files", "directory": desktop, "pattern": "*.*"})
        files = result.get("files", [])
        print(f"Found {len(files)} files")
        for i, file in enumerate(files[:5], 1):
            print(f"{i}. {file}")
        if len(files) > 5:
            print(f"...and {len(files) - 5} more files")
    
    # Test file existence
    example_file = os.path.join(desktop, "example.txt")
    print(f"\nChecking if file exists: {example_file}")
    result = file_search_handler.process_ai_command({"action": "file_exists", "path": example_file})
    exists = result.get("exists", False)
    print(f"File exists: {exists}")

def test_natural_language_search():
    """Test natural language search capabilities."""
    print("\n=== Testing Natural Language Search ===\n")
    
    queries = [
        "Find PDF files on my desktop",
        "Show me text files modified today",
        "Find documents larger than 10MB",
        "List files in my Documents folder",
        "Find Excel files created last week"
    ]
    
    for query in queries:
        print(f"\nQuery: \"{query}\"")
        response = file_search_handler.natural_language_search(query)
        print("-" * 80)
        print(response)
        print("-" * 80)

def interactive_mode():
    """Run an interactive test loop."""
    print("\n=== Interactive File Search ===\n")
    print("Enter 'q' to quit, 'nl' for natural language, 'do' for direct operations")
    
    while True:
        mode = input("\nSearch mode (nl/do/q): ").strip().lower()
        
        if mode == 'q':
            break
        elif mode == 'nl':
            query = input("Enter natural language query: ")
            response = file_search_handler.natural_language_search(query)
            print("-" * 80)
            print(response)
            print("-" * 80)
        elif mode == 'do':
            print("Available actions: list_folders, list_files, search_files_recursive, file_exists, folder_exists")
            action = input("Enter action: ").strip()
            
            if action == 'list_folders' or action == 'list_files' or action == 'search_files_recursive':
                directory = input("Enter directory path: ")
                pattern = "*" if action == 'list_folders' else input("Enter file pattern (or * for all): ")
                
                command = {"action": action, "directory": directory}
                if action != 'list_folders':
                    command["pattern"] = pattern
                
                result = file_search_handler.process_ai_command(command)
                print(json.dumps(result, indent=2))
            
            elif action == 'file_exists' or action == 'folder_exists':
                path = input("Enter file/folder path: ")
                result = file_search_handler.process_ai_command({"action": action, "path": path})
                print(json.dumps(result, indent=2))
            
            else:
                print(f"Unknown action: {action}")
        else:
            print("Unknown mode. Use 'nl' for natural language, 'do' for direct operations, or 'q' to quit")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test Everything SDK file search")
    parser.add_argument("--direct", "-d", action="store_true", help="Test direct operations")
    parser.add_argument("--natural", "-n", action="store_true", help="Test natural language search")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--query", "-q", help="Run a specific natural language query")
    
    args = parser.parse_args()
    
    # Check if Everything SDK is available
    print(f"Everything SDK available: {search_engine.available}")
    
    if args.query:
        response = file_search_handler.natural_language_search(args.query)
        print("-" * 80)
        print(response)
        print("-" * 80)
    elif args.direct:
        test_direct_operations()
    elif args.natural:
        test_natural_language_search()
    elif args.interactive:
        interactive_mode()
    else:
        # Default to running all tests
        test_direct_operations()
        test_natural_language_search()
        interactive_mode()

if __name__ == "__main__":
    main() 