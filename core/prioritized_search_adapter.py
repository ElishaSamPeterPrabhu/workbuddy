"""
Prioritized Search Adapter - Integrates SearchNavigator with the existing file search API.
This adapter ensures backward compatibility while enabling prioritized searching.
"""

import os
import re
import datetime
from typing import List, Dict, Any, Optional, Union

from core.search_navigator import search_navigator

class PrioritizedSearchAdapter:
    """
    Adapter class that provides compatibility between the SearchNavigator and
    the existing file search API.
    """
    
    def __init__(self):
        """Initialize the adapter."""
        self.default_directory = os.path.expanduser("~")  # User's home directory
    
    def search(self, 
               query: str, 
               path: Optional[str] = None, 
               file_type: Optional[str] = None,
               min_size: Optional[int] = None, 
               max_size: Optional[int] = None,
               modified_after: Optional[Union[str, datetime.datetime]] = None,
               modified_before: Optional[Union[str, datetime.datetime]] = None,
               limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for files using prioritized search.
        
        Args:
            query: The search query string
            path: Optional path to limit search to
            file_type: Optional file extension or type (pdf, doc, etc.)
            min_size: Optional minimum file size in bytes
            max_size: Optional maximum file size in bytes
            modified_after: Optional date/time for files modified after
            modified_before: Optional date/time for files modified before
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing file information
        """
        # If a specific path is provided, search only that location
        if path:
            results = search_navigator.search_location(
                location=path,
                name_pattern=query,
                file_type=file_type,
                max_depth=5,  # Deeper search when path is specified
                max_results=limit
            )
        else:
            # Do a prioritized search across all locations
            results = search_navigator.prioritized_search(
                name_pattern=query,
                file_type=file_type,
                max_results=limit,
                include_system_folders=False
            )
        
        # Filter results by size if specified
        if min_size is not None or max_size is not None:
            filtered_results = []
            for item in results:
                size = item.get("size", 0)
                if (min_size is None or size >= min_size) and (max_size is None or size <= max_size):
                    filtered_results.append(item)
            results = filtered_results
        
        # Filter results by modification date if specified
        if modified_after is not None or modified_before is not None:
            # Convert string dates to datetime objects
            if isinstance(modified_after, str):
                modified_after = datetime.datetime.fromisoformat(modified_after.replace('Z', '+00:00'))
            if isinstance(modified_before, str):
                modified_before = datetime.datetime.fromisoformat(modified_before.replace('Z', '+00:00'))
            
            filtered_results = []
            for item in results:
                date_modified = item.get("date_modified", 0)
                if isinstance(date_modified, (int, float)):
                    date_modified = datetime.datetime.fromtimestamp(date_modified)
                elif isinstance(date_modified, str):
                    try:
                        date_modified = datetime.datetime.fromisoformat(date_modified.replace('Z', '+00:00'))
                    except ValueError:
                        continue
                
                if ((modified_after is None or date_modified >= modified_after) and 
                    (modified_before is None or date_modified <= modified_before)):
                    filtered_results.append(item)
            
            results = filtered_results
        
        # Format results to match the expected API format
        formatted_results = []
        for item in results:
            # Convert date to ISO format string
            date_modified = item.get("date_modified", 0)
            if isinstance(date_modified, (int, float)):
                date_modified = datetime.datetime.fromtimestamp(date_modified).isoformat()
            
            formatted_results.append({
                "path": item.get("path", ""),
                "name": item.get("name", ""),
                "size": item.get("size", 0),
                "date_modified": date_modified,
                "is_folder": item.get("is_folder", False)
            })
        
        return formatted_results[:limit]
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return search results.
        
        Args:
            query: Natural language query from the user/AI
            
        Returns:
            Dictionary with search results and metadata
        """
        # Extract search parameters from the query
        search_params = self._parse_query(query)
        
        # Execute the search with the extracted parameters
        results = self.search(
            query=search_params.get("query", ""),
            path=search_params.get("path"),
            file_type=search_params.get("file_type"),
            min_size=search_params.get("min_size"),
            max_size=search_params.get("max_size"),
            modified_after=search_params.get("modified_after"),
            modified_before=search_params.get("modified_before"),
            limit=search_params.get("limit", 50)
        )
        
        # Format the results (keep as is since they're already formatted by search())
        return {
            "query": query,
            "parsed_params": search_params,
            "results": results,
            "count": len(results),
            "success": True
        }
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query into search parameters.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary of search parameters
        """
        params = {
            "query": "",
            "path": None,
            "file_type": None,
            "min_size": None,
            "max_size": None,
            "modified_after": None,
            "modified_before": None,
            "limit": 50
        }
        
        # Extract file types
        file_type_match = re.search(r'\.([a-zA-Z0-9]+)\b|\bfiles?\s+of\s+type\s+([a-zA-Z0-9]+)|\b([a-zA-Z0-9]+)\s+files?\b', query, re.IGNORECASE)
        if file_type_match:
            ext = file_type_match.group(1) or file_type_match.group(2) or file_type_match.group(3)
            if ext:
                params["file_type"] = ext.lower()
                # Remove the file type from the query for cleaner keyword search
                query = re.sub(r'\.([a-zA-Z0-9]+)\b|\bfiles?\s+of\s+type\s+([a-zA-Z0-9]+)|\b([a-zA-Z0-9]+)\s+files?\b', '', query, flags=re.IGNORECASE)
        
        # Extract paths - look for "in [path]" pattern
        path_match = re.search(r'\bin\s+([\'"]?)([a-zA-Z]:\\[^"\']+|~[^"\']*|\/[^"\']+)(\1)', query, re.IGNORECASE)
        if path_match:
            path = path_match.group(2)
            # Handle home directory
            if path.startswith('~'):
                path = os.path.expanduser(path)
            params["path"] = path
            # Remove the path from the query for cleaner keyword search
            query = re.sub(r'\bin\s+([\'"]?)([a-zA-Z]:\\[^"\']+|~[^"\']*|\/[^"\']+)(\1)', '', query, flags=re.IGNORECASE)
        
        # Extract time frames
        time_frames = {
            r'\btoday\b': (datetime.datetime.now().replace(hour=0, minute=0, second=0), None),
            r'\byesterday\b': ((datetime.datetime.now() - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0), datetime.datetime.now().replace(hour=0, minute=0, second=0)),
            r'\blast\s+(\d+)\s+days?\b': lambda m: (datetime.datetime.now() - datetime.timedelta(days=int(m.group(1))), None),
            r'\blast\s+week\b': (datetime.datetime.now() - datetime.timedelta(days=7), None),
            r'\blast\s+month\b': (datetime.datetime.now() - datetime.timedelta(days=30), None),
            r'\blast\s+year\b': (datetime.datetime.now() - datetime.timedelta(days=365), None)
        }
        
        for pattern, time_func in time_frames.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if callable(time_func):
                    start_time, end_time = time_func(match)
                else:
                    start_time, end_time = time_func
                
                params["modified_after"] = start_time
                if end_time:
                    params["modified_before"] = end_time
                
                # Remove the time frame from the query for cleaner keyword search
                query = re.sub(pattern, '', query, flags=re.IGNORECASE)
                break
        
        # Extract size constraints
        size_patterns = {
            r'\blarger\s+than\s+(\d+)\s*(KB|MB|GB|B)\b': 'min_size',
            r'\bsmaller\s+than\s+(\d+)\s*(KB|MB|GB|B)\b': 'max_size',
            r'\bbigger\s+than\s+(\d+)\s*(KB|MB|GB|B)\b': 'min_size',
            r'\bless\s+than\s+(\d+)\s*(KB|MB|GB|B)\b': 'max_size'
        }
        
        for pattern, param_name in size_patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                size_value = int(match.group(1))
                size_unit = match.group(2).upper()
                
                # Convert to bytes
                multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
                size_in_bytes = size_value * multipliers.get(size_unit, 1)
                
                params[param_name] = size_in_bytes
                
                # Remove the size constraint from the query
                query = re.sub(pattern, '', query, flags=re.IGNORECASE)
        
        # Extract limit
        limit_match = re.search(r'\blimit\s+(\d+)\b|\btop\s+(\d+)\b', query, re.IGNORECASE)
        if limit_match:
            limit = int(limit_match.group(1) or limit_match.group(2))
            params["limit"] = min(limit, 100)  # Cap at 100 results
            # Remove the limit from the query
            query = re.sub(r'\blimit\s+(\d+)\b|\btop\s+(\d+)\b', '', query, flags=re.IGNORECASE)
        
        # The remaining text becomes the query
        params["query"] = query.strip()
        
        # If no path specified but location mentioned, use our similar_locations feature
        if not params["path"]:
            # Check if query mentions desktop, documents, etc.
            common_locations = {
                r'\bdesktop\b': 'Desktop',
                r'\bdocuments\b': 'Documents',
                r'\bdownloads\b': 'Downloads',
                r'\bpictures\b': 'Pictures',
                r'\bmusic\b': 'Music',
                r'\bvideos\b': 'Videos'
            }
            
            for pattern, folder in common_locations.items():
                if re.search(pattern, query, re.IGNORECASE):
                    # Try to locate the folder using search_navigator
                    matches = search_navigator.find_similar_locations(folder)
                    if matches:
                        params["path"] = matches[0]  # Use the first match
                        break
        
        return params
    
    # Implement standard file operation methods
    def list_folders(self, directory: str) -> List[str]:
        """
        Return all folders in the given directory.
        
        Args:
            directory: Directory to list folders from
            
        Returns:
            List of folder names
        """
        try:
            return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
        except Exception as e:
            print(f"Error listing folders: {e}")
            return []
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        Return all files matching the pattern in the directory (non-recursive).
        
        Args:
            directory: Directory to list files from
            pattern: Pattern to match filenames
            
        Returns:
            List of file names
        """
        import fnmatch
        try:
            return [f for f in os.listdir(directory) 
                    if os.path.isfile(os.path.join(directory, f)) and fnmatch.fnmatch(f, pattern)]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def search_files_recursive(self, directory: str, pattern: str = "*") -> List[str]:
        """
        Search for files recursively in the given directory with the specified pattern.
        
        Args:
            directory: Directory to search in
            pattern: Pattern to match filenames
            
        Returns:
            List of matched file paths
        """
        import traceback
        import time
        import threading
        import fnmatch
        
        try:
            print(f"DEBUG: search_files_recursive called with directory={directory}, pattern={pattern}")
            
            # Make sure directory exists
            directory = os.path.expanduser(directory)
            if not os.path.isdir(directory):
                print(f"DEBUG: Directory does not exist: {directory}")
                return []
            
            print(f"DEBUG: Directory exists and expanded to: {directory}")
            
            # Use a faster, non-recursive approach first for common file extensions
            # This is a quick search to see if we can find obvious matches quickly
            matched_files = []
            max_time = 5  # Maximum search time in seconds
            start_time = time.time()
            
            # Quick file scan using glob which is much faster than os.walk for simple patterns
            import glob
            
            # Try direct pattern match first (fastest)
            quick_matches = glob.glob(os.path.join(directory, pattern))
            quick_matches.extend(glob.glob(os.path.join(directory, "*", pattern)))
            
            # If we found files or this is a simple pattern, use those results
            if quick_matches:
                print(f"DEBUG: Quick search found {len(quick_matches)} matches")
                return [f for f in quick_matches if os.path.isfile(f)]
            
            # Use a fallback to os.walk but with a time limit
            results = []
            search_complete = False
            
            def search_worker():
                nonlocal results, search_complete
                try:
                    # For safety, limit depth and max results
                    search_results = search_navigator.search_location(
                        location=directory,
                        name_pattern=pattern,
                        max_depth=3,  # Reduce max depth for performance
                        max_results=50  # Limit results for performance
                    )
                    # Extract just the file paths from the results
                    results = [item.get("path", "") for item in search_results 
                              if not item.get("is_folder", False)]
                    search_complete = True
                except Exception as e:
                    print(f"DEBUG: Search worker exception: {e}")
                    search_complete = True
            
            # Start search in background thread
            search_thread = threading.Thread(target=search_worker)
            search_thread.daemon = True  # Allow main thread to exit
            search_thread.start()
            
            # Wait for search to complete or timeout
            search_thread.join(max_time)
            
            if not search_complete:
                print(f"DEBUG: Search timed out after {max_time} seconds")
                # Even if timed out, return what we found so far
                return results
            
            print(f"DEBUG: Search completed, found {len(results)} files")
            return results
            
        except Exception as e:
            print(f"DEBUG: Exception in search_files_recursive: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return []
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists at the given path.
        
        Args:
            path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.isfile(path)
    
    def folder_exists(self, path: str) -> bool:
        """
        Check if a folder exists at the given path.
        
        Args:
            path: Path to check
            
        Returns:
            True if folder exists, False otherwise
        """
        return os.path.isdir(path)

# Create a singleton instance
prioritized_search = PrioritizedSearchAdapter() 