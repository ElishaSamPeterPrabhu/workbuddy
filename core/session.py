"""
Session management module for WorkBuddy.

Handles creating and managing user sessions.
"""

import os
import json
from uuid import uuid4
from typing import Dict, Any


def create_session_file(filepath: str = "cookies.json") -> Dict[str, str]:
    """
    Create a session file with unique identifiers.
    
    Args:
        filepath: Path to save the session file
        
    Returns:
        Dictionary containing session information
    """
    interlocutor_id = "workbuddy_user"
    session_id = str(uuid4())
    
    cookies = {"interlocutor_id": interlocutor_id, "session_id": session_id}
    print(f"Created new session: {cookies}")
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cookies, f)
    
    return cookies


def load_session(filepath: str = "cookies.json") -> Dict[str, str]:
    """
    Load an existing session from a file, or create a new one if not found.
    
    Args:
        filepath: Path to the session file
        
    Returns:
        Dictionary containing session information
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            return cookies
        else:
            return create_session_file(filepath)
    except Exception as e:
        print(f"Error loading session: {e}")
        return create_session_file(filepath) 