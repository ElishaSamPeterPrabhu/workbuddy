"""
Search Navigator - Advanced file system search with prioritization.
Implements a systematic approach to searching files across the filesystem.
"""

import os
import re
import string
import fnmatch
import logging
import platform
import shutil
from typing import List, Dict, Any, Optional, Union, Tuple, Set, Generator
from pathlib import Path

class SearchNavigator:
    """
    A file system navigation and search utility with prioritized search locations.
    
    This class provides methods to search for files in a systematic way, prioritizing
    common locations first and then expanding to the entire filesystem when needed.
    """
    
    def __init__(self):
        """Initialize the SearchNavigator with system-specific settings."""
        self.logger = logging.getLogger("search_navigator")
        self.system = platform.system()
        self.user_home = str(Path.home())
        
        # Initialize prioritized locations
        self._initialize_priority_locations()
        self._initialize_drive_info()
    
    def _initialize_priority_locations(self) -> None:
        """
        Initialize prioritized search locations based on OS and user directories.
        
        Sets up a tiered priority system for common folders like Desktop, Documents, etc.
        """
        self.priority_locations = {
            # Tier 1: Desktop and Documents (highest priority)
            1: [],
            # Tier 2: Downloads, Pictures, Videos, Music
            2: [],
            # Tier 3: User home directory and all immediate subfolders
            3: [self.user_home],
            # Tier 4: Root directories of all drives
            4: [],
            # Tier 5: System directories that might contain user data
            5: []
        }
        
        # Common user directories by platform
        if self.system == "Windows":
            # Windows priority locations
            common_locations = {
                1: [
                    os.path.join(self.user_home, "Desktop"),
                    os.path.join(self.user_home, "Documents"),
                    "C:\\"  # Add C:\ drive root to tier 1 for immediate searching
                ],
                2: [
                    os.path.join(self.user_home, "Downloads"),
                    os.path.join(self.user_home, "Pictures"),
                    os.path.join(self.user_home, "Videos"),
                    os.path.join(self.user_home, "Music"),
                ],
                5: [
                    os.environ.get("ProgramFiles", "C:\\Program Files"),
                    os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
                    os.environ.get("APPDATA", os.path.join(self.user_home, "AppData", "Roaming")),
                    os.environ.get("LOCALAPPDATA", os.path.join(self.user_home, "AppData", "Local")),
                ]
            }
        elif self.system == "Darwin":  # macOS
            # macOS priority locations
            common_locations = {
                1: [
                    os.path.join(self.user_home, "Desktop"),
                    os.path.join(self.user_home, "Documents"),
                ],
                2: [
                    os.path.join(self.user_home, "Downloads"),
                    os.path.join(self.user_home, "Pictures"),
                    os.path.join(self.user_home, "Movies"),
                    os.path.join(self.user_home, "Music"),
                ],
                5: [
                    "/Applications",
                    os.path.join(self.user_home, "Library"),
                ]
            }
        else:  # Linux and others
            # Linux priority locations
            common_locations = {
                1: [
                    os.path.join(self.user_home, "Desktop"),
                    os.path.join(self.user_home, "Documents"),
                ],
                2: [
                    os.path.join(self.user_home, "Downloads"),
                    os.path.join(self.user_home, "Pictures"),
                    os.path.join(self.user_home, "Videos"),
                    os.path.join(self.user_home, "Music"),
                ],
                5: [
                    "/usr/local",
                    os.path.join(self.user_home, ".local"),
                    os.path.join(self.user_home, ".config"),
                ]
            }
        
        # Add all common locations that exist
        for tier, locations in common_locations.items():
            for location in locations:
                if os.path.exists(location) and os.path.isdir(location):
                    self.priority_locations[tier].append(location)
    
    def _initialize_drive_info(self) -> None:
        """Initialize information about available drives for systematic searching."""
        self.drives = []
        
        if self.system == "Windows":
            # Get all drives on Windows
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    self.drives.append(drive)
                    # Add to tier 4 priority locations
                    self.priority_locations[4].append(drive)
        else:
            # On Unix-like systems, just add root
            self.drives.append("/")
            self.priority_locations[4].append("/")
    
    def get_drive_usage(self) -> Dict[str, Dict[str, Any]]:
        """
        Get usage statistics for all drives.
        
        Returns:
            Dictionary mapping drive paths to usage statistics
        """
        result = {}
        for drive in self.drives:
            try:
                if os.path.exists(drive):
                    total, used, free = shutil.disk_usage(drive)
                    result[drive] = {
                        "total": total,
                        "used": used,
                        "free": free,
                        "percent_used": (used / total) * 100 if total > 0 else 0
                    }
            except Exception as e:
                self.logger.error(f"Error getting drive usage for {drive}: {e}")
        return result
    
    def get_priority_locations(self) -> Dict[int, List[str]]:
        """
        Get the current priority locations configuration.
        
        Returns:
            Dictionary mapping priority tiers to lists of locations
        """
        return self.priority_locations
    
    def search_location(self, 
                       location: str, 
                       name_pattern: Optional[str] = None,
                       file_type: Optional[str] = None,
                       max_depth: int = 3,
                       max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search a specific location for files matching criteria.
        
        Args:
            location: Directory to search in
            name_pattern: Pattern to match filenames against
            file_type: File extension to filter by (without the dot)
            max_depth: Maximum folder depth to search
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries with file information
        """
        results = []
        count = 0
        
        if not os.path.exists(location) or not os.path.isdir(location):
            return results
        
        # Compile regex pattern if provided
        pattern_regex = None
        if name_pattern:
            try:
                pattern_regex = re.compile(name_pattern, re.IGNORECASE)
            except re.error:
                # If it's not a valid regex, use it as a glob pattern
                pass
        
        # Normalize file type
        if file_type and not file_type.startswith('.'):
            file_type = f".{file_type}"
        
        # Track current depth
        for current_depth, (root, dirs, files) in enumerate(self._walk_max_depth(location, max_depth)):
            # Check max results
            if count >= max_results:
                break
            
            # Process files in this directory
            for file in files:
                # Check max results
                if count >= max_results:
                    break
                
                # Check if file matches pattern
                file_matches = True
                if pattern_regex:
                    try:
                        file_matches = bool(pattern_regex.search(file))
                    except Exception:
                        # Fallback to glob matching
                        file_matches = fnmatch.fnmatch(file.lower(), name_pattern.lower())
                elif name_pattern:
                    file_matches = fnmatch.fnmatch(file.lower(), name_pattern.lower())
                
                # Check file type if specified
                if file_matches and file_type:
                    file_matches = file.lower().endswith(file_type.lower())
                
                if file_matches:
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        results.append({
                            "path": file_path,
                            "name": file,
                            "size": stat.st_size,
                            "date_modified": stat.st_mtime,
                            "is_folder": False,
                            "priority_level": self._get_location_priority(root)
                        })
                        count += 1
                    except Exception as e:
                        self.logger.error(f"Error accessing file {file_path}: {e}")
        
        return results
    
    def prioritized_search(self, 
                          name_pattern: Optional[str] = None,
                          file_type: Optional[str] = None,
                          max_results: int = 100,
                          include_system_folders: bool = False) -> List[Dict[str, Any]]:
        """
        Search for files using the prioritized location system.
        
        This method searches through locations in priority order until it finds enough results
        or exhausts all priority locations.
        
        Args:
            name_pattern: Pattern to match filenames against
            file_type: File extension to filter by (without the dot)
            max_results: Maximum number of results to return
            include_system_folders: Whether to include system folders in the search
            
        Returns:
            List of dictionaries with file information, sorted by priority
        """
        all_results = []
        remaining_results = max_results
        
        # Search through each priority tier
        for tier in range(1, 6):
            # Skip system folders (tier 5) if not requested
            if tier == 5 and not include_system_folders:
                continue
                
            # Set depth based on tier (higher depth for higher priority locations)
            max_depth = 6 - tier  # Tier 1 gets depth 5, Tier 5 gets depth 1
            
            for location in self.priority_locations[tier]:
                # Skip if we have enough results
                if remaining_results <= 0:
                    break
                    
                # Search this location
                tier_results = self.search_location(
                    location=location,
                    name_pattern=name_pattern,
                    file_type=file_type,
                    max_depth=max_depth,
                    max_results=remaining_results
                )
                
                # Add results and update remaining count
                all_results.extend(tier_results)
                remaining_results -= len(tier_results)
        
        # Sort results by priority level (lower is better)
        all_results.sort(key=lambda x: (x.get("priority_level", 999), -x.get("date_modified", 0)))
        
        return all_results[:max_results]
    
    def _walk_max_depth(self, path: str, max_depth: int) -> Generator[Tuple[str, List[str], List[str]], None, None]:
        """
        Walk a directory tree up to a maximum depth.
        
        Args:
            path: Starting path
            max_depth: Maximum depth to walk
            
        Yields:
            Tuples of (dirpath, dirnames, filenames) for each directory up to max_depth
        """
        path = path.rstrip(os.path.sep)
        assert os.path.isdir(path)
        num_sep = path.count(os.path.sep)
        for root, dirs, files in os.walk(path):
            yield root, dirs, files
            current_depth = root.count(os.path.sep) - num_sep
            if current_depth >= max_depth:
                # Clear dirs to prevent going deeper
                dirs.clear()
    
    def _get_location_priority(self, path: str) -> int:
        """
        Get the priority level for a given path.
        
        Args:
            path: Path to check
            
        Returns:
            Priority level (1-5, lower is better)
        """
        for tier, locations in self.priority_locations.items():
            for location in locations:
                if path.startswith(location):
                    return tier
        return 999  # Unknown location gets lowest priority
    
    def find_similar_locations(self, partial_path: str) -> List[str]:
        """
        Find locations that match a partial path.
        
        This is useful for helping users discover the correct path when they only
        remember part of it.
        
        Args:
            partial_path: Partial path to match
            
        Returns:
            List of matching locations
        """
        matches = []
        partial_path_lower = partial_path.lower()
        
        # Search in all priority locations
        for tier in range(1, 6):
            for location in self.priority_locations[tier]:
                if partial_path_lower in location.lower():
                    matches.append(location)
                
                # Check immediate subdirectories too
                try:
                    for item in os.listdir(location):
                        item_path = os.path.join(location, item)
                        if os.path.isdir(item_path) and partial_path_lower in item_path.lower():
                            matches.append(item_path)
                except Exception:
                    pass
        
        return matches

# Create a singleton instance
search_navigator = SearchNavigator() 