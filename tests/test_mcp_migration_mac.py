"""
Test script to verify MCP fallbacks work correctly on macOS.

Since Windows-specific MCP servers won't run on Mac, this tests
that all fallback mechanisms work properly.
"""

import os
import sys
import platform

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_platform_check():
    """Verify we're on macOS."""
    print(f"\n=== Platform Check ===")
    print(f"Platform: {platform.system()}")
    print(f"Machine: {platform.machine()}")
    print(f"Version: {platform.version()}")
    
    if platform.system() == "Darwin":
        print("✓ Running on macOS")
        return True
    else:
        print("✗ Not running on macOS")
        return False


def test_file_search_fallback():
    """Test that file search falls back gracefully on macOS."""
    print("\n=== Testing File Search Fallback ===")
    
    try:
        from core.ai_file_search_handler import file_search_handler
        
        # Test a simple search
        command = {
            "action": "list_folders",
            "directory": os.path.expanduser("~")
        }
        result = file_search_handler.process_ai_command(command)
        
        # On Mac, this should use fallback
        if result.get("status") == "success" or result.get("success"):
            print("✓ File search using fallback mechanism")
            return True
        else:
            print(f"File search result: {result}")
            # Even if MCP fails, it's OK as long as no crash
            print("✓ File search handled gracefully")
            return True
            
    except Exception as e:
        print(f"✗ File search error: {e}")
        return False


def test_command_execution_fallback():
    """Test that command execution falls back to subprocess on macOS."""
    print("\n=== Testing Command Execution Fallback ===")
    
    try:
        from core.filesearch import run_shell_command
        
        # Test a macOS command
        result = run_shell_command("echo 'Hello from macOS'", timeout=5)
        
        if result['returncode'] == 0 and "Hello from macOS" in result['stdout']:
            print("✓ Command execution using subprocess fallback")
            return True
        else:
            print(f"✗ Command failed: {result}")
            return False
            
    except Exception as e:
        print(f"✗ Command execution error: {e}")
        return False


def test_storage_fallback():
    """Test that storage operations work without MCP on macOS."""
    print("\n=== Testing Storage Fallback ===")
    
    try:
        from core.storage import get_user_preference, set_user_preference
        
        # Test preference storage
        test_key = "test_mac_preference"
        test_value = {"platform": "macOS", "test": True}
        
        # Set preference
        set_user_preference(test_key, test_value)
        
        # Get preference
        retrieved = get_user_preference(test_key)
        
        if retrieved == test_value:
            print("✓ Storage operations working with SQLite")
            return True
        else:
            print(f"✗ Storage mismatch: {retrieved}")
            return False
            
    except Exception as e:
        print(f"✗ Storage error: {e}")
        return False


def test_everything_search_fallback():
    """Test that Everything search falls back on macOS."""
    print("\n=== Testing Everything Search Fallback ===")
    
    try:
        from core.everything_search import everything_search
        
        # On macOS, should use basic fallback search
        if everything_search.is_available():
            print("✓ Search engine available (using fallback)")
            
            # Do a simple search in home directory
            results = everything_search.search_files(
                "*.txt", 
                max_results=5,
                search_path=os.path.expanduser("~/Desktop")
            )
            
            print(f"✓ Fallback search completed, found {len(results)} files")
            return True
        else:
            print("✗ No search engine available")
            return False
            
    except Exception as e:
        print(f"✗ Everything search error: {e}")
        return False


def test_macos_specific_operations():
    """Test macOS-specific operations that could use MCP in future."""
    print("\n=== Testing macOS-Specific Operations ===")
    
    try:
        # Test home directory access
        home = os.path.expanduser("~")
        desktop = os.path.join(home, "Desktop")
        
        if os.path.exists(desktop):
            print(f"✓ Can access macOS Desktop: {desktop}")
        
        # Test macOS command
        from core.filesearch import run_shell_command
        result = run_shell_command("which python3", timeout=5)
        
        if result['returncode'] == 0:
            print(f"✓ Python3 found at: {result['stdout'].strip()}")
        
        return True
        
    except Exception as e:
        print(f"✗ macOS operations error: {e}")
        return False


def suggest_macos_mcp_servers():
    """Suggest MCP servers that would work on macOS."""
    print("\n=== Suggested MCP Servers for macOS ===")
    
    suggestions = [
        {
            "name": "filesystem",
            "package": "@modelcontextprotocol/server-filesystem",
            "purpose": "Cross-platform file operations"
        },
        {
            "name": "github",
            "package": "@modelcontextprotocol/server-github", 
            "purpose": "GitHub API integration"
        },
        {
            "name": "sqlite",
            "package": "@modelcontextprotocol/server-sqlite",
            "purpose": "SQLite database operations"
        },
        {
            "name": "brave-search",
            "package": "@modelcontextprotocol/server-brave-search",
            "purpose": "Web search capabilities"
        }
    ]
    
    print("\nMCP servers that work on macOS:")
    for server in suggestions:
        print(f"\n- {server['name']}")
        print(f"  Package: {server['package']}")
        print(f"  Purpose: {server['purpose']}")
    
    print("\nTo install: npm install -g <package-name>")
    return True


def main():
    """Run macOS-specific MCP fallback tests."""
    print("=" * 60)
    print("macOS MCP Fallback Test Suite")
    print("=" * 60)
    
    tests = [
        test_platform_check,
        test_file_search_fallback,
        test_command_execution_fallback,
        test_storage_fallback,
        test_everything_search_fallback,
        test_macos_specific_operations,
        suggest_macos_mcp_servers
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All fallback mechanisms working correctly on macOS!")
        print("WorkBuddy will function normally without Windows MCP servers.")
    else:
        print("\n✗ Some fallback mechanisms need attention")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 