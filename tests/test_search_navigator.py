"""
Test script for the SearchNavigator prioritized file search system.
This script demonstrates the prioritized search capabilities and performance.
"""

import os
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.search_navigator import search_navigator

def print_results(results: List[Dict[str, Any]], query: str, runtime: float) -> None:
    """
    Print search results in a formatted way.
    
    Args:
        results: List of result dictionaries
        query: The original search query
        runtime: Time taken for the search in seconds
    """
    print("\n" + "="*80)
    count = len(results)
    print(f"Search Results: {count} items found for '{query}' (in {runtime:.3f} seconds)")
    print("="*80)
    
    if results:
        # Group by priority level
        by_priority = {}
        for item in results:
            priority = item.get("priority_level", 999)
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(item)
        
        # Print results grouped by priority
        for priority in sorted(by_priority.keys()):
            items = by_priority[priority]
            priority_name = {
                1: "Desktop & Documents",
                2: "Downloads, Pictures, etc.",
                3: "Home Directory",
                4: "Drive Roots",
                5: "System Folders",
                999: "Other Locations"
            }.get(priority, f"Priority {priority}")
            
            print(f"\n--- {priority_name} ({len(items)} items) ---")
            
            # Print top items in this priority
            for i, item in enumerate(items[:5], 1):
                name = item.get("name", "")
                path = item.get("path", "")
                size = item.get("size", 0)
                # Format size
                if size < 1024:
                    size_str = f"{size} bytes"
                elif size < 1024**2:
                    size_str = f"{size/1024:.1f} KB"
                elif size < 1024**3:
                    size_str = f"{size/1024**2:.1f} MB"
                else:
                    size_str = f"{size/1024**3:.1f} GB"
                    
                print(f"{i}. {name} ({size_str})")
                print(f"   Path: {path}")
            
            if len(items) > 5:
                print(f"   ...and {len(items) - 5} more items in this priority level")
    else:
        print("No results found.")

def show_priority_locations() -> None:
    """Display the priority locations configured in the SearchNavigator."""
    print("\n" + "="*80)
    print("Configured Priority Locations")
    print("="*80)
    
    priority_locations = search_navigator.get_priority_locations()
    
    for tier in sorted(priority_locations.keys()):
        locations = priority_locations[tier]
        tier_name = {
            1: "Tier 1 - Highest Priority (Desktop & Documents)",
            2: "Tier 2 - High Priority (Downloads, Pictures, etc.)",
            3: "Tier 3 - Medium Priority (Home Directory)",
            4: "Tier 4 - Low Priority (Drive Roots)",
            5: "Tier 5 - Lowest Priority (System Folders)"
        }.get(tier, f"Tier {tier}")
        
        print(f"\n--- {tier_name} ---")
        if locations:
            for i, location in enumerate(locations, 1):
                exists = "✓" if os.path.exists(location) else "✗"
                print(f"{i}. {location} ({exists})")
        else:
            print("No locations configured for this tier.")

def search_by_name(name_pattern: str, file_type: Optional[str] = None) -> None:
    """
    Search for files by name pattern and optional file type.
    
    Args:
        name_pattern: Pattern to match against filenames
        file_type: Optional file extension to filter by
    """
    print(f"\nSearching for files matching '{name_pattern}'{f' with type {file_type}' if file_type else ''}...")
    
    start_time = time.time()
    results = search_navigator.prioritized_search(
        name_pattern=name_pattern,
        file_type=file_type,
        max_results=100,
        include_system_folders=False
    )
    end_time = time.time()
    
    print_results(results, name_pattern, end_time - start_time)

def search_by_example(example_number: int) -> None:
    """
    Run a predefined example search.
    
    Args:
        example_number: Example number to run (1-5)
    """
    examples = [
        {"name": "*.pdf", "type": None, "description": "All PDF files in priority locations"},
        {"name": "*.docx", "type": None, "description": "All Word documents in priority locations"},
        {"name": "report*", "type": None, "description": "Files starting with 'report'"},
        {"name": "*data*", "type": "csv", "description": "CSV files with 'data' in the name"},
        {"name": "*.py", "type": None, "description": "All Python files in priority locations"}
    ]
    
    if 1 <= example_number <= len(examples):
        example = examples[example_number - 1]
        print(f"\nRunning Example {example_number}: {example['description']}")
        search_by_name(example["name"], example["type"])
    else:
        print(f"Example {example_number} not found. Available examples: 1-{len(examples)}")

def show_examples() -> None:
    """Display available example searches."""
    print("\n" + "="*80)
    print("Example Searches")
    print("="*80)
    
    examples = [
        "All PDF files in priority locations",
        "All Word documents in priority locations",
        "Files starting with 'report'",
        "CSV files with 'data' in the name",
        "All Python files in priority locations"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")

def show_drive_info() -> None:
    """Display information about available drives."""
    print("\n" + "="*80)
    print("Drive Information")
    print("="*80)
    
    drive_usage = search_navigator.get_drive_usage()
    
    for drive, usage in drive_usage.items():
        print(f"\n--- {drive} ---")
        total_gb = usage.get("total", 0) / (1024**3)
        used_gb = usage.get("used", 0) / (1024**3)
        free_gb = usage.get("free", 0) / (1024**3)
        percent = usage.get("percent_used", 0)
        
        print(f"Total: {total_gb:.2f} GB")
        print(f"Used:  {used_gb:.2f} GB ({percent:.1f}%)")
        print(f"Free:  {free_gb:.2f} GB")

def main() -> None:
    """Main function to process command line arguments and run tests."""
    parser = argparse.ArgumentParser(description="Test the SearchNavigator prioritized search system")
    
    # Search options
    parser.add_argument("--search", "-s", help="Search pattern for filenames")
    parser.add_argument("--type", "-t", help="File type/extension to filter by")
    
    # Information options
    parser.add_argument("--locations", "-l", action="store_true", help="Show priority locations")
    parser.add_argument("--drives", "-d", action="store_true", help="Show drive information")
    parser.add_argument("--examples", "-e", action="store_true", help="Show example searches")
    parser.add_argument("--run-example", "-r", type=int, help="Run a specific example (1-5)")
    
    args = parser.parse_args()
    
    # If no arguments, show usage information
    if not any(vars(args).values()):
        parser.print_help()
        print("\nTry --examples to see available example searches.")
        return
    
    # Show priority locations if requested
    if args.locations:
        show_priority_locations()
    
    # Show drive information if requested
    if args.drives:
        show_drive_info()
    
    # Show example searches if requested
    if args.examples:
        show_examples()
    
    # Run a specific example if requested
    if args.run_example:
        search_by_example(args.run_example)
    
    # Run a search if pattern provided
    if args.search:
        search_by_name(args.search, args.type)

if __name__ == "__main__":
    main() 