"""
Compare various file search methods for WorkBuddy.
This script compares the original file search to our new prioritized search.
"""

import os
import time
import json
import argparse
from typing import Dict, Any, List

# Import the search implementations
from core.everything_search import search_engine
from core.file_search_adapter import file_search
from core.prioritized_search_adapter import prioritized_search

def run_search_comparison(query: str) -> None:
    """
    Run a search using both search methods and compare results.
    
    Args:
        query: Search query to test
    """
    print(f"Comparing search methods for query: '{query}'")
    print("="*80)
    
    # Test original search
    print("\n[1] Testing original search implementation...")
    start_time = time.time()
    original_results = file_search.process_query(query)
    original_time = time.time() - start_time
    original_count = original_results.get("count", 0)
    
    print(f"Found {original_count} results in {original_time:.3f} seconds")
    
    # Test prioritized search
    print("\n[2] Testing prioritized search implementation...")
    start_time = time.time()
    prioritized_results = prioritized_search.process_query(query)
    prioritized_time = time.time() - start_time
    prioritized_count = prioritized_results.get("count", 0)
    
    print(f"Found {prioritized_count} results in {prioritized_time:.3f} seconds")
    
    # Compare top results
    print("\n--- Top 5 Results Comparison ---")
    
    print("\nOriginal Search Results:")
    for i, item in enumerate(original_results.get("results", [])[:5], 1):
        print(f"{i}. {item.get('name', '')} - {item.get('path', '')}")
    
    print("\nPrioritized Search Results:")
    for i, item in enumerate(prioritized_results.get("results", [])[:5], 1):
        print(f"{i}. {item.get('name', '')} - {item.get('path', '')}")
    
    # Performance comparison
    print("\n--- Performance Comparison ---")
    speedup = original_time / prioritized_time if prioritized_time > 0 else float('inf')
    print(f"Original search: {original_time:.3f} seconds")
    print(f"Prioritized search: {prioritized_time:.3f} seconds")
    print(f"Speed difference: {speedup:.2f}x {('faster' if speedup > 1 else 'slower')}")

def run_example_queries() -> None:
    """Run example queries to demonstrate search capabilities."""
    examples = [
        "Find PDF files",
        "Find text files on Desktop",
        "Find Python files in Documents",
        "Find image files",
        "Find large files"
    ]
    
    for i, query in enumerate(examples, 1):
        print(f"\n\nExample {i}: {query}")
        print("-"*80)
        run_search_comparison(query)

def main() -> None:
    """Main function to process command line arguments and run tests."""
    parser = argparse.ArgumentParser(description="Compare file search methods")
    
    parser.add_argument("--query", "-q", help="Search query to test")
    parser.add_argument("--examples", "-e", action="store_true", help="Run example queries")
    
    args = parser.parse_args()
    
    if args.query:
        run_search_comparison(args.query)
    elif args.examples:
        run_example_queries()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 