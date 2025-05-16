"""
Test script for the Everything SDK file search implementation.
Run this script to test file search functionality with natural language queries.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any

from core.ai_file_search_handler import file_search_handler

def print_results(results: Dict[str, Any]) -> None:
    """Print search results in a readable format."""
    if not results.get("success", False):
        print(f"Error: {results.get('error', 'Unknown error')}")
        return
    
    print("\n" + "="*80)
    print(f"Search Results ({results.get('count', 0)} items found)")
    print("="*80)
    
    if "results" in results:
        # Process_query results
        for i, item in enumerate(results["results"][:15], 1):
            print(f"{i}. {item.get('name', '')}")
            print(f"   Path: {item.get('path', '')}")
            print(f"   Size: {item.get('size', '')}")
            print(f"   Modified: {item.get('date_modified', '')}")
            print()
        
        if results.get("count", 0) > 15:
            print(f"...and {results.get('count', 0) - 15} more items.")
    
    elif "files" in results:
        # List_files or search_files_recursive results
        files = results["files"]
        for i, file in enumerate(files[:15], 1):
            print(f"{i}. {os.path.basename(file)}")
            print(f"   Path: {file}")
        
        if len(files) > 15:
            print(f"...and {len(files) - 15} more files.")
    
    elif "folders" in results:
        # List_folders results
        folders = results["folders"]
        for i, folder in enumerate(folders[:15], 1):
            print(f"{i}. {folder}")
        
        if len(folders) > 15:
            print(f"...and {len(folders) - 15} more folders.")
    
    elif "exists" in results:
        # File_exists or folder_exists results
        path = results.get("path", "")
        exists = results.get("exists", False)
        print(f"Path: {path}")
        print(f"Exists: {exists}")
    
    print("\n" + "="*80)

def process_natural_language_query(query: str, verbose: bool = False) -> None:
    """Process a natural language query and print formatted results."""
    # Get the natural language response
    response = file_search_handler.natural_language_search(query)
    print("\n" + "="*80)
    print("Natural Language Response:")
    print("="*80)
    print(response)
    
    # If verbose, also show the raw results
    if verbose:
        results = file_search_handler.handle_request("process_query", query=query)
        print("\n" + "="*80)
        print("Raw Results:")
        print("="*80)
        if "parsed_params" in results:
            print("Parsed Parameters:")
            for key, value in results["parsed_params"].items():
                print(f"  {key}: {value}")
        print_results(results)

def process_command(command_str: str) -> None:
    """Process a JSON command and print results."""
    try:
        # Parse the command
        command = json.loads(command_str)
        
        # Process the command
        results = file_search_handler.process_ai_command(command)
        
        # Print the results
        print_results(results)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON command.")
    except Exception as e:
        print(f"Error processing command: {e}")

def show_examples() -> None:
    """Show example queries and commands."""
    print("\n" + "="*80)
    print("Example Natural Language Queries:")
    print("="*80)
    examples = [
        "Find PDF files in Documents",
        "Show me text files on my Desktop",
        "Find files larger than 10MB",
        "Search for files modified today",
        "Look for files with 'report' in the name",
        "Show me images from last week",
        "Find Excel files in Downloads",
        "Show all Python files in my projects folder",
        "Find files containing the word 'budget'"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    print("\n" + "="*80)
    print("Example JSON Commands:")
    print("="*80)
    commands = [
        {"action": "list_folders", "directory": str(Path.home())},
        {"action": "list_files", "directory": str(Path.home() / "Desktop"), "pattern": "*.txt"},
        {"action": "search_files_recursive", "directory": str(Path.home() / "Documents"), "pattern": "*.pdf"},
        {"action": "file_exists", "path": str(Path.home() / "Desktop" / "example.txt")},
        {"action": "process_query", "query": "Find large files in Documents"}
    ]
    
    for i, command in enumerate(commands, 1):
        print(f"{i}. {json.dumps(command, indent=2)}")

def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Test Everything SDK file search")
    parser.add_argument("--query", "-q", help="Natural language query")
    parser.add_argument("--command", "-c", help="JSON command")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    parser.add_argument("--examples", "-e", action="store_true", help="Show example queries and commands")
    
    args = parser.parse_args()
    
    # Show examples if requested or no arguments provided
    if args.examples or (not args.query and not args.command):
        show_examples()
    
    # Process query if provided
    if args.query:
        process_natural_language_query(args.query, args.verbose)
    
    # Process command if provided
    if args.command:
        process_command(args.command)

if __name__ == "__main__":
    main() 