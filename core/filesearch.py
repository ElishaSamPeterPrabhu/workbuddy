"""
File search and command execution module for WorkBuddy (Jarvis Assistant).

Allows running dynamic shell commands (with safety checks) as returned by the AI, capturing output for file search and related tasks.
"""

import subprocess
import shlex
import time
from typing import List, Optional, Dict, Any
import logging
import platform


def run_shell_command(
    command: str, cwd: Optional[str] = None, timeout: int = 30
) -> Dict[str, Any]:
    """
    Run a shell command safely, capture stdout and stderr, and return the results.
    On Windows, always use shell=True for 'dir' commands (shell built-in).
    Prints timing and all outputs for debugging.

    Args:
        command (str): The shell command to run.
        cwd (Optional[str]): The working directory to run the command in.
        timeout (int): Timeout in seconds for the command.

    Returns:
        Dict[str, Any]: { 'stdout': ..., 'stderr': ..., 'returncode': ... }
    """
    print(f"Running shell command: {command}")
    print(f"Working directory: {cwd or 'current'}")
    start_time = time.time()
    try:
        if platform.system() == "Windows":
            # Always use shell=True for dir (shell built-in)
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        else:
            # On Unix, shell=True is usually fine
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        elapsed = time.time() - start_time
        print(f"Command finished in {elapsed:.2f} seconds")
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired as e:
        logging.error(f"Command timed out: {command}")
        print(f"Timeout: {e}")
        return {"stdout": "", "stderr": f"Timeout: {e}", "returncode": -1}
    except Exception as e:
        logging.error(f"Command execution error: {e}")
        print(f"Execution error: {e}")
        return {"stdout": "", "stderr": str(e), "returncode": -1}
