"""
File search adapter for integrating the Everything search engine with AI.
This module translates natural language queries into Everything search parameters.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

# Import the Everything search engine
from core.everything_search import search_engine

class FileSearchAdapter:
    """
    Adapter class that translates between AI requests and the Everything search engine.
    """
    
    def __init__(self):
        """Initialize the FileSearchAdapter."""
        self.search_engine = search_engine
        self.default_directory = os.path.expanduser("~")  # User's home directory
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return search results.
        
        Args:
            query: Natural language query from the user/AI
            
        Returns:
            Dictionary with search results and metadata
        """
        # Parse the query to extract search parameters
        search_params = self._parse_query(query)
        
        # Execute the search
        results = self.search_engine.search(
            query=search_params.get("query", ""),
            path=search_params.get("path"),
            file_type=search_params.get("file_type"),
            min_size=search_params.get("min_size"),
            max_size=search_params.get("max_size"),
            modified_after=search_params.get("modified_after"),
            modified_before=search_params.get("modified_before"),
            limit=search_params.get("limit", 50)
        )
        
        # Format the results
        formatted_results = self._format_results(results, search_params)
        
        return {
            "query": query,
            "parsed_params": search_params,
            "results": formatted_results,
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
            r'\btoday\b': (datetime.now().replace(hour=0, minute=0, second=0), None),
            r'\byesterday\b': ((datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0), datetime.now().replace(hour=0, minute=0, second=0)),
            r'\blast\s+(\d+)\s+days?\b': lambda m: (datetime.now() - timedelta(days=int(m.group(1))), None),
            r'\blast\s+week\b': (datetime.now() - timedelta(days=7), None),
            r'\blast\s+month\b': (datetime.now() - timedelta(days=30), None),
            r'\blast\s+year\b': (datetime.now() - timedelta(days=365), None)
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
        
        # If no path specified, use user's home directory
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
                    user_folder = os.path.join(self.default_directory, folder)
                    if os.path.exists(user_folder):
                        params["path"] = user_folder
                        break
        
        return params
    
    def _format_results(self, results: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format search results for presentation.
        
        Args:
            results: List of result dictionaries
            params: Search parameters used
            
        Returns:
            Formatted results list
        """
        formatted = []
        for item in results:
            # Format file size for display
            size_bytes = item.get("size", 0)
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024**2:
                size_str = f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024**3:
                size_str = f"{size_bytes/1024**2:.1f} MB"
            else:
                size_str = f"{size_bytes/1024**3:.1f} GB"
            
            # Format date for display
            date_str = item.get("date_modified", "")
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    pass
            
            formatted.append({
                "name": item.get("name", ""),
                "path": item.get("path", ""),
                "size": size_str,
                "date_modified": date_str,
                "is_folder": item.get("is_folder", False)
            })
        
        return formatted
    
    # Implement the file API functions to maintain compatibility
    def list_folders(self, directory: str) -> List[str]:
        """
        Return all folders in the given directory.
        
        Args:
            directory: Directory to list folders from
            
        Returns:
            List of folder names
        """
        return self.search_engine.list_folders(directory)
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        Return all files matching the pattern in the directory (non-recursive).
        
        Args:
            directory: Directory to list files from
            pattern: Pattern to match filenames
            
        Returns:
            List of file names
        """
        return self.search_engine.list_files(directory, pattern)
    
    def search_files_recursive(self, directory: str, pattern: str = "*") -> List[str]:
        """
        Return all files matching the pattern in the directory and all subfolders.
        
        Args:
            directory: Directory to search in
            pattern: Pattern to match filenames
            
        Returns:
            List of file paths
        """
        return self.search_engine.search_files_recursive(directory, pattern)
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists at the given path.
        
        Args:
            path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        return self.search_engine.file_exists(path)
    
    def folder_exists(self, path: str) -> bool:
        """
        Check if a folder exists at the given path.
        
        Args:
            path: Path to check
            
        Returns:
            True if folder exists, False otherwise
        """
        return self.search_engine.folder_exists(path)

# Create a singleton instance
file_search = FileSearchAdapter() 