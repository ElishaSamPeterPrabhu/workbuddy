"""
File search implementation using the Everything SDK.
Provides a clean, simple interface for searching files on Windows.
"""

import os
import re
import datetime
from typing import List, Dict, Any, Optional, Union

class EverythingSearch:
    """
    A wrapper class for the Everything SDK that provides advanced file search capabilities.
    
    This class provides methods to search for files using the Everything search engine,
    which is much faster than native file system searches on Windows.
    """
    
    def __init__(self):
        """Initialize the EverythingSearch class."""
        try:
            from pyeverything import Everything
            self.es = Everything()
            self.available = True
        except ImportError:
            print("Warning: pyeverything not installed. Falling back to slower file system search.")
            self.available = False
            self.es = None
    
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
        Search for files using Everything SDK.
        
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
        if not self.available:
            return self._fallback_search(query, path, file_type, limit)
        
        try:
            # Build Everything search query
            search_query = []
            
            # Add the basic query if not empty
            if query and query.strip():
                search_query.append(query)
            
            # Add path filter
            if path:
                path = path.replace('\\', '/')
                search_query.append(f'path:"{path}"')
            
            # Add file type filter
            if file_type:
                if not file_type.startswith('.'):
                    file_type = f'.{file_type}'
                search_query.append(f'ext:{file_type[1:]}')
            
            # Add size filters
            if min_size is not None:
                search_query.append(f'size:>{min_size}')
            if max_size is not None:
                search_query.append(f'size:<{max_size}')
            
            # Add date filters
            if modified_after:
                if isinstance(modified_after, str):
                    modified_after = datetime.datetime.fromisoformat(modified_after.replace('Z', '+00:00'))
                date_str = modified_after.strftime('%Y-%m-%d')
                search_query.append(f'dm:>{date_str}')
            
            if modified_before:
                if isinstance(modified_before, str):
                    modified_before = datetime.datetime.fromisoformat(modified_before.replace('Z', '+00:00'))
                date_str = modified_before.strftime('%Y-%m-%d')
                search_query.append(f'dm:<{date_str}')
            
            # Combine all query parts
            final_query = ' '.join(search_query)
            
            # Execute search
            self.es.search(final_query)
            
            # Process results
            results = []
            for item in self.es.results()[:limit]:
                # Convert date to ISO format string
                date_modified = item.date_modified
                if isinstance(date_modified, datetime.datetime):
                    date_modified = date_modified.isoformat()
                
                results.append({
                    "path": item.path,
                    "name": os.path.basename(item.path),
                    "size": item.size,
                    "date_modified": date_modified,
                    "is_folder": os.path.isdir(item.path)
                })
            
            return results
            
        except Exception as e:
            print(f"Everything search error: {e}")
            return self._fallback_search(query, path, file_type, limit)
    
    def _fallback_search(self, query: str, path: Optional[str] = None, 
                        file_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fallback to standard file system search if Everything SDK fails or is not available.
        
        Args:
            query: Search query
            path: Path to search in
            file_type: File extension to filter by
            limit: Maximum results to return
            
        Returns:
            List of dictionaries containing file information
        """
        results = []
        search_path = path or os.path.expanduser("~")
        query_regex = re.compile(query, re.IGNORECASE) if query else None
        
        try:
            count = 0
            for root, dirs, files in os.walk(search_path):
                # Check if we've reached the limit
                if count >= limit:
                    break
                
                # Process files in this directory
                for file in files:
                    # Check if we've reached the limit
                    if count >= limit:
                        break
                    
                    # Check if file matches query
                    if query_regex and not query_regex.search(file):
                        continue
                    
                    # Check file type if specified
                    if file_type and not file.lower().endswith(file_type.lower()):
                        continue
                    
                    # Get file details
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        date_modified = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                        
                        results.append({
                            "path": file_path,
                            "name": file,
                            "size": stat.st_size,
                            "date_modified": date_modified,
                            "is_folder": False
                        })
                        count += 1
                    except Exception as e:
                        print(f"Error accessing file {file_path}: {e}")
            
            return results
        
        except Exception as e:
            print(f"Fallback search error: {e}")
            return []
    
    def search_by_content(self, content: str, path: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for files containing specific content (text).
        Note: Only works with Everything SDK and requires Everything with content indexing enabled.
        
        Args:
            content: The content to search for
            path: Optional path to limit search to
            limit: Maximum number of results
            
        Returns:
            List of dictionaries containing file information
        """
        if not self.available:
            print("Content search requires Everything SDK")
            return []
        
        try:
            query_parts = []
            if content:
                query_parts.append(f'content:"{content}"')
            if path:
                path = path.replace('\\', '/')
                query_parts.append(f'path:"{path}"')
            
            final_query = ' '.join(query_parts)
            self.es.search(final_query)
            
            results = []
            for item in self.es.results()[:limit]:
                # Convert date to ISO format string
                date_modified = item.date_modified
                if isinstance(date_modified, datetime.datetime):
                    date_modified = date_modified.isoformat()
                
                results.append({
                    "path": item.path,
                    "name": os.path.basename(item.path),
                    "size": item.size,
                    "date_modified": date_modified,
                    "is_folder": os.path.isdir(item.path)
                })
            
            return results
            
        except Exception as e:
            print(f"Content search error: {e}")
            return []

    def list_folders(self, directory: str) -> List[str]:
        """
        Return all folders in the given directory.
        
        Args:
            directory: The directory to list folders from
            
        Returns:
            List of folder names
        """
        if not self.available:
            try:
                return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
            except Exception as e:
                print(f"Error listing folders: {e}")
                return []
        
        try:
            self.es.search(f'path:"{directory}" folder:')
            return [os.path.basename(item.path) for item in self.es.results()]
        except Exception as e:
            print(f"Error listing folders: {e}")
            try:
                return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
            except Exception:
                return []
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        Return all files matching the pattern in the directory (non-recursive).
        
        Args:
            directory: The directory to list files from
            pattern: Wildcard pattern to filter files
            
        Returns:
            List of file names
        """
        if not self.available:
            import fnmatch
            try:
                return [f for f in os.listdir(directory) 
                        if os.path.isfile(os.path.join(directory, f)) and fnmatch.fnmatch(f, pattern)]
            except Exception as e:
                print(f"Error listing files: {e}")
                return []
        
        try:
            # Convert * wildcard to Everything format
            query = pattern.replace('*', '')
            self.es.search(f'path:"{directory}" file: {query}')
            return [os.path.basename(item.path) for item in self.es.results()]
        except Exception as e:
            print(f"Error listing files: {e}")
            import fnmatch
            try:
                return [f for f in os.listdir(directory) 
                        if os.path.isfile(os.path.join(directory, f)) and fnmatch.fnmatch(f, pattern)]
            except Exception:
                return []
    
    def search_files_recursive(self, directory: str, pattern: str = "*") -> List[str]:
        """
        Return all files matching the pattern in the directory and all subfolders (recursive).
        
        Args:
            directory: The directory to search in
            pattern: Pattern to match filenames
            
        Returns:
            List of file paths
        """
        if not self.available:
            matches = []
            import fnmatch
            try:
                for root, dirs, files in os.walk(directory):
                    for filename in fnmatch.filter(files, pattern):
                        matches.append(os.path.join(root, filename))
                return matches
            except Exception as e:
                print(f"Error searching files: {e}")
                return []
        
        try:
            # Convert * wildcard to Everything format
            query = pattern.replace('*', '')
            self.es.search(f'path:"{directory}" file: {query}')
            return [item.path for item in self.es.results()]
        except Exception as e:
            print(f"Error searching files: {e}")
            matches = []
            import fnmatch
            try:
                for root, dirs, files in os.walk(directory):
                    for filename in fnmatch.filter(files, pattern):
                        matches.append(os.path.join(root, filename))
                return matches
            except Exception:
                return []
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists at the given path.
        
        Args:
            path: Path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.isfile(path)
    
    def folder_exists(self, path: str) -> bool:
        """
        Check if a folder exists at the given path.
        
        Args:
            path: Path to the folder
            
        Returns:
            True if folder exists, False otherwise
        """
        return os.path.isdir(path)

# Create a singleton instance
search_engine = EverythingSearch() 