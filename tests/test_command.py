"""
Test script for running shell commands.
Provides a cross-platform way to execute shell commands in tests.
"""

import os
import platform
import shlex
import subprocess
import time
from typing import Any, Dict, Optional


def run_shell_command(
    command: str, cwd: Optional[str] = None, timeout: int = 30
) -> Dict[str, Any]:
    """
    Run a shell command and return its output.
    
    Args:
        command: Command string to execute
        cwd: Working directory (optional)
        timeout: Timeout in seconds
        
    Returns:
        Dictionary with stdout, stderr, and return code
    """
    print(f"Running shell command: {command}")
    print(f"Working directory: {cwd or 'current'}")
    start_time = time.time()

    try:
        if platform.system() == "Windows":
            # shell=True and string command is usually safest on Windows
            result = subprocess.run(
                command,
                shell=True,  # Must be True if using string
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        else:
            # On Unix, prefer shlex.split() + shell=False
            cmd_list = shlex.split(command)
            result = subprocess.run(
                cmd_list,
                shell=False,
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
        print(f"Command timed out: {command}")
        print(f"Timeout: {e}")
        return {"stdout": "", "stderr": f"Timeout: {e}", "returncode": -1}

    except Exception as e:
        print(f"Command execution error: {e}")
        return {"stdout": "", "stderr": str(e), "returncode": -1}


if __name__ == "__main__":
    command = "dir"
    cwd = "C:\\Users\\eprabhu\\Desktop"
    result = run_shell_command(command, cwd)
    print(result) 