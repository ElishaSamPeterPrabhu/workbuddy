from typing import List
import os
import fnmatch


def list_folders(directory: str) -> List[str]:
    """Return all folders in the given directory."""
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, f))
    ]


def list_files(directory: str, pattern: str = "*") -> List[str]:
    """Return all files matching the pattern in the directory (non-recursive)."""
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if fnmatch.fnmatch(f, pattern) and os.path.isfile(os.path.join(directory, f))
    ]


def search_files_recursive(directory: str, pattern: str = "*") -> List[str]:
    """Return all files matching the pattern in the directory and all subfolders (recursive)."""
    matches = []
    for root, _, files in os.walk(directory):
        for f in files:
            if fnmatch.fnmatch(f, pattern):
                matches.append(os.path.join(root, f))
    return matches


def list_subfolders(directory: str, depth: int = 1) -> List[str]:
    """Return all subfolders up to the specified depth."""
    result = []

    def _walk(current: str, current_depth: int):
        if current_depth > depth:
            return
        try:
            for entry in os.listdir(current):
                full_path = os.path.join(current, entry)
                if os.path.isdir(full_path):
                    result.append(full_path)
                    _walk(full_path, current_depth + 1)
        except Exception:
            pass

    _walk(directory, 1)
    return result


def file_exists(path: str) -> bool:
    """Return True if the file exists at the given path."""
    return os.path.isfile(path)
