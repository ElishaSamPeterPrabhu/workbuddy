"""
Controller for orchestrating AI-driven, multi-round file search sessions in WorkBuddy.
"""

from typing import List, Tuple, TYPE_CHECKING
from core.file_search_session import FileSearchSession
import os

if TYPE_CHECKING:
    from core.ai_client import AIClient


def resolve_directory(directory: str) -> str:
    """
    Convert AI-suggested directory names to absolute paths.
    """
    if not directory:
        return os.getcwd()
    d = directory.strip().lower()
    if d == "desktop":
        return os.path.join(os.path.expanduser("~"), "Desktop")
    if d in [".", "./"]:
        return os.getcwd()
    # If it's a Windows path, ensure it's valid
    return os.path.abspath(directory)


def get_candidate_directories() -> List[str]:
    """
    Return a list of user-accessible, likely folders for file search.
    Uses Windows Known Folders API (if available), environment variables, and all direct subfolders of the user's home directory.
    Also loads user-configured search roots from config if present.
    """
    home = os.path.expanduser("~")
    candidates = set()

    # Try to use Windows Known Folders API for Desktop/Documents
    try:
        import winshell

        candidates.add(winshell.desktop())
        candidates.add(winshell.my_documents())
    except ImportError:
        # Fallback: try common names
        pass
    except Exception as e:
        print(f"[WARNING] winshell error: {e}")

    # Use environment variables for Downloads, etc.
    downloads = os.path.join(os.environ.get("USERPROFILE", home), "Downloads")
    if os.path.isdir(downloads):
        candidates.add(downloads)

    # Add all direct subfolders of home (dynamic, no hardcoding)
    try:
        for entry in os.listdir(home):
            full_path = os.path.join(home, entry)
            if os.path.isdir(full_path) and not entry.startswith("."):
                candidates.add(full_path)
    except Exception as e:
        print(f"[WARNING] Could not list subfolders in {home}: {e}")

    # Add current working directory
    candidates.add(os.getcwd())

    # Load user-configured search roots from config file (if present)
    config_path = os.path.join(home, ".workbuddy_search_roots.txt")
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and os.path.isdir(line):
                        candidates.add(line)
        except Exception as e:
            print(f"[WARNING] Could not read user search roots config: {e}")

    # Only include directories that actually exist and are accessible
    return [d for d in candidates if os.path.isdir(d) and os.access(d, os.R_OK)]


def expand_subfolders(directory: str) -> list[str]:
    """
    Return a list of all first-level subfolders of the given directory.
    """
    try:
        return [
            os.path.join(directory, entry)
            for entry in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, entry))
        ]
    except Exception as e:
        print(f"[WARNING] Could not expand subfolders for {directory}: {e}")
        return []


def enumerate_subfolders(parent: str, pattern: str = "*", depth: int = 1) -> list[str]:
    """
    Recursively enumerate subfolders of 'parent' up to 'depth', matching 'pattern'.
    Returns a list of absolute paths.
    """
    import fnmatch

    result = []

    def _walk(current, current_depth):
        if current_depth > depth:
            return
        try:
            for entry in os.listdir(current):
                full_path = os.path.join(current, entry)
                if os.path.isdir(full_path) and fnmatch.fnmatch(entry, pattern):
                    result.append(full_path)
                    _walk(full_path, current_depth + 1)
        except Exception as e:
            print(f"[WARNING] Could not enumerate subfolders for {current}: {e}")

    _walk(parent, 1)
    return result


def ai_file_search_loop(
    user_query: str, ai_client: "AIClient"
) -> Tuple[str, List[str]]:
    """
    Run a multi-round, AI-driven file search session with dynamic candidate directory support.
    Returns the final AI stop message and the list of found files.
    """
    session = FileSearchSession(user_query)
    ai_message = "File search complete."
    candidate_dirs = get_candidate_directories()
    searched_dirs = set()
    expanded_dirs = set()
    while session.should_continue():
        available_dirs = [d for d in candidate_dirs if d not in searched_dirs]
        exhausted = not available_dirs
        context = {
            "user_query": session.user_query,
            "last_results": session.get_last_results(),
            "history": session.get_history(),
            "round": session.round,
            "candidate_directories": available_dirs,
            "searched_directories": list(searched_dirs),
            "exhausted_candidates": exhausted,
        }
        command = ai_client.get_file_search_command(context)
        # NEW: Handle candidate_directory_request
        if command.get("action") == "candidate_directory_request":
            parent = resolve_directory(command.get("parent_directory"))
            pattern = command.get("pattern", "*")
            depth = int(command.get("depth", 1))
            candidate_dirs = enumerate_subfolders(parent, pattern, depth)
            searched_dirs = set()  # Optionally reset for new round
            print(f"[System] Updated candidate directories: {candidate_dirs}")
            session.round += 1
            session.history.append(
                {
                    "round": session.round,
                    "note": f"Enumerated subfolders of {parent} (pattern: {pattern}, depth: {depth})",
                }
            )
            continue
        pattern = command.get("pattern")
        directory = resolve_directory(command.get("directory"))
        subfolders = command.get("subfolders", False)
        new_dirs = command.get("add_candidate_directories")
        if new_dirs and isinstance(new_dirs, list):
            for d in new_dirs:
                abs_d = resolve_directory(d)
                if os.path.isdir(abs_d) and abs_d not in candidate_dirs:
                    candidate_dirs.append(abs_d)
        if subfolders and directory not in expanded_dirs:
            subfolder_list = expand_subfolders(directory)
            for sub in subfolder_list:
                if sub not in candidate_dirs:
                    candidate_dirs.append(sub)
            expanded_dirs.add(directory)
            session.round += 1
            session.history.append(
                {
                    "round": session.round,
                    "pattern": pattern,
                    "directory": directory,
                    "results": [],
                    "note": "Expanded subfolders.",
                }
            )
            continue
        if directory not in available_dirs:
            print(
                f"[WARNING] AI suggested directory not in available candidate_directories: {directory}. Skipping this round."
            )
            session.round += 1
            session.history.append(
                {
                    "round": session.round,
                    "pattern": pattern,
                    "directory": directory,
                    "results": [],
                }
            )
            continue
        searched_dirs.add(directory)
        session.run_search_round(pattern, directory)
        if len([d for d in candidate_dirs if d not in searched_dirs]) == 0:
            ai_message = (
                "All candidate directories have been searched. "
                "You may add new folders to search or choose next steps."
            )
            break
    return ai_message, session.get_last_results()


def run_file_search_interactive(
    user_query: str, ai_client: "AIClient"
) -> Tuple[str, List[str]]:
    """
    Run the AI-driven file search loop interactively, printing each step and command to the console.
    Supports dynamic candidate directory requests.
    Returns the AI stop message and the list of found file paths.
    """
    print(f"[WorkBuddy] Starting file search for: {user_query}")
    session = FileSearchSession(user_query)
    ai_message = "File search complete."
    candidate_dirs = get_candidate_directories()
    searched_dirs = set()
    expanded_dirs = set()
    while session.should_continue():
        available_dirs = [d for d in candidate_dirs if d not in searched_dirs]
        exhausted = not available_dirs
        context = {
            "user_query": session.user_query,
            "last_results": session.get_last_results(),
            "history": session.get_history(),
            "round": session.round,
            "candidate_directories": available_dirs,
            "searched_directories": list(searched_dirs),
            "exhausted_candidates": exhausted,
        }
        command = ai_client.get_file_search_command(context)
        # NEW: Handle candidate_directory_request
        if command.get("action") == "candidate_directory_request":
            parent = resolve_directory(command.get("parent_directory"))
            pattern = command.get("pattern", "*")
            depth = int(command.get("depth", 1))
            candidate_dirs = enumerate_subfolders(parent, pattern, depth)
            searched_dirs = set()
            print(f"[System] Updated candidate directories: {candidate_dirs}")
            session.round += 1
            session.history.append(
                {
                    "round": session.round,
                    "note": f"Enumerated subfolders of {parent} (pattern: {pattern}, depth: {depth})",
                }
            )
            continue
        pattern = command.get("pattern")
        directory = resolve_directory(command.get("directory"))
        subfolders = command.get("subfolders", False)
        new_dirs = command.get("add_candidate_directories")
        if new_dirs and isinstance(new_dirs, list):
            for d in new_dirs:
                abs_d = resolve_directory(d)
                if os.path.isdir(abs_d) and abs_d not in candidate_dirs:
                    candidate_dirs.append(abs_d)
        if subfolders and directory not in expanded_dirs:
            subfolder_list = expand_subfolders(directory)
            for sub in subfolder_list:
                if sub not in candidate_dirs:
                    candidate_dirs.append(sub)
            expanded_dirs.add(directory)
            session.round += 1
            session.history.append(
                {
                    "round": session.round,
                    "pattern": pattern,
                    "directory": directory,
                    "results": [],
                    "note": "Expanded subfolders.",
                }
            )
            continue
        if directory not in available_dirs:
            print(
                f"[WARNING] AI suggested directory not in available candidate_directories: {directory}. Skipping this round."
            )
            session.round += 1
            session.history.append(
                {
                    "round": session.round,
                    "pattern": pattern,
                    "directory": directory,
                    "results": [],
                }
            )
            continue
        searched_dirs.add(directory)
        results = session.run_search_round(pattern, directory)
        print(f"[System] Results ({len(results)}): {results}")
        if len([d for d in candidate_dirs if d not in searched_dirs]) == 0:
            ai_message = (
                "All candidate directories have been searched. "
                "You may add new folders to search or choose next steps."
            )
            print(f"[AI] Stopping: {ai_message}")
            break
    print(
        f"[WorkBuddy] File search complete. Final results: {session.get_last_results()}"
    )
    return ai_message, session.get_last_results()
