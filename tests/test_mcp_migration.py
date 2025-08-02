"""
Test script to verify MCP migrations are working correctly.

This script tests the migrated modules to ensure they work with MCP
and fall back gracefully when MCP is not available.
"""

import os
import sys
import asyncio
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_file_search_handler():
    """Test the MCP-based file search handler."""
    print("\n=== Testing File Search Handler ===")
    
    try:
        from core.ai_file_search_handler import file_search_handler
        
        # Test natural language search
        result = file_search_handler.natural_language_search("find python files")
        print(f"Natural language search result: {result}")
        
        # Test specific command
        command = {
            "action": "list_folders",
            "directory": os.path.expanduser("~")
        }
        result = file_search_handler.process_ai_command(command)
        print(f"List folders result: {result}")
        
        print("✓ File search handler working")
        return True
        
    except Exception as e:
        print(f"✗ File search handler error: {e}")
        return False


def test_command_execution():
    """Test MCP-based command execution."""
    print("\n=== Testing Command Execution ===")
    
    try:
        from core.filesearch import run_shell_command
        
        # Test simple command
        result = run_shell_command("echo Hello from MCP", timeout=5)
        print(f"Command result: {result}")
        
        if result['returncode'] == 0:
            print("✓ Command execution working")
            return True
        else:
            print(f"✗ Command failed: {result}")
            return False
            
    except Exception as e:
        print(f"✗ Command execution error: {e}")
        return False


def test_storage_mcp():
    """Test MCP-aware storage operations."""
    print("\n=== Testing Storage MCP Operations ===")
    
    try:
        from core.storage import read_config_file_mcp, write_config_file_mcp
        
        # Test data
        test_file = "test_mcp_config.json"
        test_data = {"test": "MCP storage test", "timestamp": str(asyncio.get_event_loop().time())}
        
        # Run async operations
        async def test_async():
            # Write test
            success = await write_config_file_mcp(test_file, test_data)
            if success:
                print("✓ MCP write successful")
            else:
                print("✗ MCP write failed")
                return False
            
            # Read test
            data = await read_config_file_mcp(test_file)
            if data and data.get("test") == "MCP storage test":
                print("✓ MCP read successful")
                return True
            else:
                print("✗ MCP read failed")
                return False
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_async())
        loop.close()
        
        # Clean up
        try:
            os.remove(test_file)
        except:
            pass
        
        return result
        
    except Exception as e:
        print(f"✗ Storage MCP error: {e}")
        return False


def test_everything_search():
    """Test Everything search with MCP fallback."""
    print("\n=== Testing Everything Search ===")
    
    try:
        from core.everything_search import everything_search
        
        # Check availability
        if everything_search.is_available():
            print("✓ Search engine available")
            
            # Test search
            results = everything_search.search_files("*.txt", max_results=5)
            print(f"Found {len(results)} text files")
            
            return True
        else:
            print("✗ No search engine available")
            return False
            
    except Exception as e:
        print(f"✗ Everything search error: {e}")
        return False


def test_mcp_manager():
    """Test MCP manager directly."""
    print("\n=== Testing MCP Manager ===")
    
    try:
        from core.mcp_manager import mcp_manager
        
        # Check configuration
        print(f"MCP config path: {mcp_manager.config_path}")
        print(f"Configured servers: {list(mcp_manager.config.get('servers', {}).keys())}")
        
        # Test server status
        async def check_servers():
            for server_name in mcp_manager.config.get('servers', {}):
                if mcp_manager.config['servers'][server_name].get('enabled', False):
                    if server_name in mcp_manager.servers:
                        print(f"✓ {server_name} server is running")
                    else:
                        print(f"- {server_name} server not started (will start on demand)")
                else:
                    print(f"- {server_name} server is disabled")
            
            return True
        
        # Run async check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(check_servers())
        loop.close()
        
        return result
        
    except Exception as e:
        print(f"✗ MCP manager error: {e}")
        return False


def main():
    """Run all MCP migration tests."""
    print("=" * 60)
    print("MCP Migration Test Suite")
    print("=" * 60)
    
    tests = [
        test_mcp_manager,
        test_file_search_handler,
        test_command_execution,
        test_storage_mcp,
        test_everything_search
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
        print("\n✓ All MCP migrations working correctly!")
    else:
        print("\n✗ Some MCP features need attention")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 