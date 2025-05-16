"""
Test script to search for a specific file using AI File Search Handler.
Also checks AI integration with the search handler.
"""

from core.ai_file_search_handler import file_search_handler
import time
import json
from typing import Optional, Dict, Any, List


class MockAIClient:
    """Mock AI client for testing if no real AI client is available."""
    
    def __init__(self) -> None:
        """Initialize the mock AI client."""
        self.last_prompt: Optional[str] = None
        self.calls: int = 0
    
    def get_response(self, prompt: str) -> str:
        """
        Mock response from AI.
        
        Args:
            prompt: The prompt to process
            
        Returns:
            A formatted response
        """
        self.last_prompt = prompt
        self.calls += 1
        
        # Extract context from the prompt if it's in the expected format
        context_str = prompt.replace("Format these file search results as a helpful response: ", "")
        try:
            context = json.loads(context_str)
            query = context.get("query", "unknown query")
            count = context.get("count", 0)
            results = context.get("results", [])
            
            if count == 0:
                return f"[AI Response] I searched for '{query}' but couldn't find any matching files."
            
            response = f"[AI Response] I found {count} files matching '{query}':\n"
            for i, item in enumerate(results[:3], 1):
                name = item.get("name", "")
                path = item.get("path", "")
                response += f"{i}. {name} (located at {path})\n"
            
            if count > 3:
                response += f"...and {count - 3} more results."
            
            return response
        except:
            return f"[AI Response] I processed your search request: '{prompt}'"


def main() -> None:
    """Search for the check_colab file and display results."""
    print("Testing AI File Search Handler\n" + "="*40)
    
    # Check if AI client is available
    print("Checking AI client availability...")
    original_ai_client = file_search_handler.ai_client
    has_ai_client = original_ai_client is not None
    
    print(f"AI client available: {has_ai_client}")
    
    # If no AI client, add a mock one temporarily
    if not has_ai_client:
        print("Adding mock AI client for testing...")
        mock_ai = MockAIClient()
        file_search_handler.ai_client = mock_ai
    
    search_query = "find check_colab file"
    print(f"\nSearch query: '{search_query}'")
    
    # Method 1: Using natural language search
    print("\n1. Using natural_language_search:")
    start_time = time.time()
    result = file_search_handler.natural_language_search(search_query)
    search_time = time.time() - start_time
    
    print(f"Result (completed in {search_time:.3f} seconds):")
    print(result)
    
    # Check if AI was used for formatting
    if not has_ai_client and isinstance(file_search_handler.ai_client, MockAIClient):
        if file_search_handler.ai_client.calls > 0:
            print("\nAI client was called successfully!")
            print(f"Prompt received by AI: {file_search_handler.ai_client.last_prompt[:100]}...")
        else:
            print("\nWARNING: AI client was not called during the search process.")
            print("The natural_language_search method might not be using the AI client properly.")
    
    # Method 2: Using direct command
    print("\n2. Using direct file search command:")
    command = {
        "action": "search",
        "query": "check_colab"
    }
    
    start_time = time.time()
    result = file_search_handler.process_ai_command(command)
    command_time = time.time() - start_time
    
    print(f"Result (completed in {command_time:.3f} seconds):")
    print(f"Found {result.get('count', 0)} results")
    
    # Show results detail
    if result.get("count", 0) > 0:
        for i, item in enumerate(result.get("results", []), 1):
            name = item.get("name", "")
            path = item.get("path", "")
            size = item.get("size", "")
            date = item.get("date_modified", "")
            
            print(f"\n{i}. {name} ({size})")
            print(f"   Path: {path}")
            print(f"   Modified: {date}")
    
    # Method 3: Search in Desktop specifically
    print("\n3. Searching specifically in Desktop:")
    command = {
        "action": "search_files_recursive",
        "directory": "C:/Users/eprabhu/Desktop",
        "pattern": "*check_colab*"
    }
    
    start_time = time.time()
    result = file_search_handler.process_ai_command(command)
    desktop_time = time.time() - start_time
    
    print(f"Result (completed in {desktop_time:.3f} seconds):")
    print(f"Found {result.get('count', 0)} results")
    
    if result.get("count", 0) > 0:
        for i, file_path in enumerate(result.get("files", []), 1):
            print(f"{i}. {file_path}")
    
    # Test direct AI formatting with search results
    if not has_ai_client and isinstance(file_search_handler.ai_client, MockAIClient):
        print("\n4. Testing direct AI formatting of search results:")
        mock_results = {
            "query": "check_colab test query",
            "results": [
                {"name": "check_colab.txt", "path": "C:/Users/eprabhu/Desktop/check_colab.txt"}
            ],
            "count": 1
        }
        
        # Reset call counter
        file_search_handler.ai_client.calls = 0
        
        # Format through AI
        ai_prompt = f"Format these file search results as a helpful response: {json.dumps(mock_results)}"
        ai_response = file_search_handler.ai_client.get_response(ai_prompt)
        
        print(f"AI Response: {ai_response}")
        print(f"AI was called: {file_search_handler.ai_client.calls > 0}")
    
    # Restore original AI client
    if not has_ai_client:
        print("\nRestoring original AI client configuration...")
        file_search_handler.ai_client = original_ai_client


if __name__ == "__main__":
    main() 