"""
AI File Search Handler - Main entry point for file search functionality.
Handles integration between the AI client and file search system.
"""

import json
from typing import Dict, Any, Optional

# Use the prioritized search implementation
from core.prioritized_search_adapter import prioritized_search

class AIFileSearchHandler:
    """
    Handles file search requests from the AI client and returns formatted results.
    """
    
    def __init__(self, ai_client=None):
        """
        Initialize the file search handler.
        
        Args:
            ai_client: Optional AI client for enhanced responses
        """
        self.file_search = prioritized_search  # Use the prioritized search adapter
        self.ai_client = ai_client
    
    def handle_request(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Handle a file search request with the specified action.
        
        Args:
            action: Action to perform (process_query, list_folders, etc.)
            **kwargs: Action-specific parameters
            
        Returns:
            Dictionary with results and status
        """
        print(f"DEBUG: handle_request called with action={action}, kwargs={kwargs}")
        try:
            if action == "process_query":
                query = kwargs.get("query", "")
                if not query:
                    return {"success": False, "error": "No query provided"}
                
                print(f"DEBUG: Processing query: {query}")
                return self.file_search.process_query(query)
                
            elif action == "list_folders":
                directory = kwargs.get("directory", "")
                if not directory:
                    return {"success": False, "error": "No directory provided"}
                
                print(f"DEBUG: Listing folders in: {directory}")
                folders = self.file_search.list_folders(directory)
                return {
                    "success": True,
                    "directory": directory,
                    "folders": folders,
                    "count": len(folders)
                }
                
            elif action == "list_files":
                directory = kwargs.get("directory", "")
                pattern = kwargs.get("pattern", "*")
                if not directory:
                    return {"success": False, "error": "No directory provided"}
                
                print(f"DEBUG: Listing files in: {directory} with pattern: {pattern}")
                files = self.file_search.list_files(directory, pattern)
                return {
                    "success": True,
                    "directory": directory,
                    "pattern": pattern,
                    "files": files,
                    "count": len(files)
                }
                
            elif action == "search_files_recursive":
                directory = kwargs.get("directory", "")
                pattern = kwargs.get("pattern", "*")
                if not directory:
                    return {"success": False, "error": "No directory provided"}
                
                print(f"DEBUG: Searching files recursively in: {directory} with pattern: {pattern}")
                files = self.file_search.search_files_recursive(directory, pattern)
                print(f"DEBUG: Found {len(files)} files matching pattern")
                return {
                    "success": True,
                    "directory": directory,
                    "pattern": pattern,
                    "files": files,
                    "count": len(files)
                }
                
            elif action == "file_exists":
                path = kwargs.get("path", "")
                if not path:
                    return {"success": False, "error": "No path provided"}
                
                exists = self.file_search.file_exists(path)
                return {
                    "success": True,
                    "path": path,
                    "exists": exists
                }
                
            elif action == "folder_exists":
                path = kwargs.get("path", "")
                if not path:
                    return {"success": False, "error": "No path provided"}
                
                exists = self.file_search.folder_exists(path)
                return {
                    "success": True,
                    "path": path,
                    "exists": exists
                }
                
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            import traceback
            print(f"DEBUG: Exception in handle_request: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}
    
    def process_ai_command(self, command: Dict[str, Any], timeout: int = 5) -> Dict[str, Any]:
        """
        Process a command from the AI and execute the appropriate file search action.
        
        Args:
            command: Dictionary with 'action' and parameters
            timeout: Maximum time in seconds to wait for search results (default: 5)
            
        Returns:
            Dictionary with results and status
        """
        print(f"DEBUG: process_ai_command called with command={command}, timeout={timeout}")
        import threading
        import time
        
        try:
            if not isinstance(command, dict):
                # Try to parse JSON if string
                if isinstance(command, str):
                    try:
                        command = json.loads(command)
                        print(f"DEBUG: Parsed command from JSON string: {command}")
                    except:
                        print("DEBUG: Failed to parse command as JSON")
                        return {"success": False, "error": "Invalid command format"}
                else:
                    print(f"DEBUG: Command is not a dict or string: {type(command)}")
                    return {"success": False, "error": "Command must be a dictionary or JSON string"}
            
            # Get the action from the command
            action = command.get("action")
            if not action:
                print("DEBUG: No action specified in command")
                return {"success": False, "error": "No action specified"}
            
            print(f"DEBUG: Action from command: {action}")
            
            # Map the AI command actions to handler actions
            action_mapping = {
                "list_folders": "list_folders",
                "list_files": "list_files",
                "search_files_recursive": "search_files_recursive",
                "file_exists": "file_exists",
                "folder_exists": "folder_exists",
                "search": "process_query",
                "find": "process_query"
            }
            
            handler_action = action_mapping.get(action, action)
            print(f"DEBUG: Mapped action to handler action: {action} -> {handler_action}")
            
            # Remove action from kwargs
            kwargs = {k: v for k, v in command.items() if k != "action" and k != "continue_search" and k != "extended_search"}
            print(f"DEBUG: Kwargs after removing action and control fields: {kwargs}")
            
            # Special case for natural language queries
            if handler_action == "process_query" and "query" not in kwargs:
                if "text" in kwargs:
                    kwargs["query"] = kwargs.pop("text")
                    print(f"DEBUG: Using 'text' as query: {kwargs['query']}")
                elif "message" in kwargs:
                    kwargs["query"] = kwargs.pop("message")
                    print(f"DEBUG: Using 'message' as query: {kwargs['query']}")
                elif "pattern" in kwargs and "directory" in kwargs:
                    # Convert file-pattern-directory to a query
                    pattern = kwargs.pop("pattern")
                    directory = kwargs.pop("directory")
                    kwargs["query"] = f"Find files matching {pattern} in {directory}"
                    print(f"DEBUG: Created query from pattern and directory: {kwargs['query']}")
            
            # Execute the search with the specified timeout
            result = self._search_with_timeout(handler_action, kwargs, timeout)
            
            # Add information about the search context
            result["directory"] = kwargs.get("directory", "")
            result["pattern"] = kwargs.get("pattern", "")
            
            # Mark if this was an extended search
            if command.get("extended_search", False):
                result["search_phase"] = "extended"
            else:
                result["search_phase"] = "quick"
                
            return result
                
        except Exception as e:
            import traceback
            print(f"DEBUG: Exception in process_ai_command: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}
    
    def continue_search(self, original_command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Continue a search that was previously started but timed out.
        This method uses a longer timeout for more extensive searching.
        
        Args:
            original_command: The original search command to continue
            
        Returns:
            Dictionary with search results
        """
        print(f"DEBUG: Continuing search with command: {original_command}")
        
        try:
            # Extract the action and parameters from the original command
            action = original_command.get("action")
            
            # Map AI command actions to handler actions
            action_mapping = {
                "list_folders": "list_folders",
                "list_files": "list_files",
                "search_files_recursive": "search_files_recursive",
                "file_exists": "file_exists",
                "folder_exists": "folder_exists",
                "search": "process_query",
                "find": "process_query"
            }
            
            handler_action = action_mapping.get(action, action)
            
            # Extract parameters (without action)
            kwargs = {k: v for k, v in original_command.items() if k != "action"}
            
            # Use a longer timeout for the extended search
            extended_timeout = 30  # 30 seconds for extended search
            print(f"DEBUG: Starting extended search with {extended_timeout}s timeout")
            
            # Perform the extended search
            result = self._search_with_timeout(handler_action, kwargs, extended_timeout)
            
            # Mark this as an extended search result
            result["search_phase"] = "extended"
            return result
            
        except Exception as e:
            import traceback
            print(f"DEBUG: Exception in continue_search: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}
    
    def _search_with_timeout(self, action: str, kwargs: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """
        Execute a search operation with a timeout.
        
        Args:
            action: The search action to perform
            kwargs: Parameters for the search
            timeout: Maximum time to wait (in seconds)
            
        Returns:
            Dictionary with search results or timeout indication
        """
        import threading
        import time
        
        print(f"DEBUG: _search_with_timeout called with action={action}, timeout={timeout}")
        
        # Default result in case of timeout
        result = {
            "success": False, 
            "error": f"Search timed out after {timeout} seconds",
            "count": 0,
            "files": [],
            "directory": kwargs.get("directory", ""),
            "pattern": kwargs.get("pattern", "")
        }
        
        search_complete = False
        
        def search_worker():
            nonlocal result, search_complete
            try:
                result = self.handle_request(action, **kwargs)
                search_complete = True
            except Exception as e:
                import traceback
                print(f"DEBUG: Search worker exception: {e}")
                print(f"DEBUG: {traceback.format_exc()}")
                result = {"success": False, "error": f"Search error: {str(e)}"}
                search_complete = True
        
        # Start search in background thread
        search_thread = threading.Thread(target=search_worker)
        search_thread.daemon = True
        start_time = time.time()
        search_thread.start()
        
        # Wait for the thread to complete or timeout
        search_thread.join(timeout)
        
        if not search_complete:
            print(f"DEBUG: Search operation timed out after {timeout} seconds")
        else:
            print(f"DEBUG: Search completed in {time.time() - start_time:.2f} seconds")
            
        return result
    
    def natural_language_search(self, query: str) -> str:
        """
        Perform a natural language search and return a human-readable response.
        
        Args:
            query: Natural language query string
            
        Returns:
            Human-readable response string
        """
        try:
            # Process the query
            result = self.file_search.process_query(query)
            
            # If using AI client and it's available, let it format the response
            if self.ai_client:
                try:
                    context = {
                        "query": query,
                        "results": result.get("results", []),
                        "count": result.get("count", 0),
                        "parameters": result.get("parsed_params", {})
                    }
                    print(f"Context: {context}")
                    return self.ai_client.get_response(
                        f"Format these file search results as a helpful response: {json.dumps(context)}"
                    )
                except Exception as e:
                    print(f"AI client error: {e}")
                    # Fall back to default formatting
            
            # Default formatting
            count = result.get("count", 0)
            results = result.get("results", [])
            
            if count == 0:
                return f"No files found matching '{query}'."
            
            response = [f"Found {count} items matching '{query}':"]
            
            # Format results
            for i, item in enumerate(results[:10], 1):
                name = item.get("name", "")
                path = item.get("path", "")
                size = item.get("size", "")
                date = item.get("date_modified", "")
                
                response.append(f"{i}. {name} ({size}, {date})")
                response.append(f"   Path: {path}")
            
            if count > 10:
                response.append(f"...and {count - 10} more items.")
            
            return "\n".join(response)
            
        except Exception as e:
            return f"Error searching for files: {e}"

# Create a singleton instance
file_search_handler = AIFileSearchHandler() 