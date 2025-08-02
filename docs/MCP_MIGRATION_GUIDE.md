# MCP Migration Guide for WorkBuddy

This guide documents the migration of WorkBuddy's Windows operations to use the Model Context Protocol (MCP) for enhanced security and modularity.

## Overview

WorkBuddy has been updated to use MCP servers for file operations, command execution, and Windows integrations. This provides:
- **Enhanced Security**: Sandboxed operations with path validation
- **Better Modularity**: Plug-and-play MCP servers
- **Unified Interface**: Consistent API for all system operations
- **Future-proof**: Ready for new MCP servers as they become available

## Modules Migrated

### 1. File Search Handler (`core/ai_file_search_handler.py`)
**Previous**: Direct file system operations using `os.walk`, `glob`, etc.
**Now**: MCP filesystem server for all file operations

Key changes:
- `list_folders()` - Uses MCP `list_directory` with filtering
- `search_files()` - Recursive search through MCP
- `file_exists()` - MCP stat operation
- `read_file()` - MCP file reading
- Async operations with sync wrappers for compatibility

### 2. Storage Module (`core/storage.py`)
**Previous**: Direct file I/O for configuration files
**Now**: MCP-aware operations with fallback

New functions:
- `read_config_file_mcp()` - Read JSON config via MCP
- `write_config_file_mcp()` - Write JSON config via MCP
- Maintains direct database access (SQLite requires local file)

### 3. Command Execution (`core/filesearch.py`)
**Previous**: Direct `subprocess.run()` calls
**Now**: MCP Windows CLI server for secure execution

Features:
- Command blocking for security
- Shell type detection (cmd/powershell/bash)
- Async and sync versions available
- Fallback to subprocess if MCP unavailable

### 4. Everything Search (`core/everything_search.py`)
**Previous**: Everything SDK as primary search method
**Now**: MCP as primary, Everything SDK as performance enhancement

Search hierarchy:
1. Try MCP filesystem search (secure, sandboxed)
2. Fall back to Everything SDK (if available)
3. Last resort: Basic file system walk

### 5. Session Management (`core/session.py`)
**Previous**: Direct file operations for conversation storage
**Now**: MCP-aware file operations

Updates:
- `save_conversation()` - Uses MCP for writing
- `load_conversation()` - Uses MCP for reading
- Async versions provided

### 6. Notifications (`core/notifications.py`)
**Previous**: Direct icon path checking
**Now**: MCP-aware but maintains direct access for system icons

Note: Windows notifications require local file paths, so icon files must be accessible locally.

### 7. Setup Startup (`setup_startup.py`)
**Previous**: Direct COM operations
**Future**: Can migrate to MCP COM server

Added TODO comments for future migration when MCP COM server is stable.

## MCP Servers Used

### 1. Filesystem MCP Server
- **Purpose**: Secure file operations
- **Features**: Path validation, sandboxing
- **Operations**: read, write, list, search, stat

### 2. Windows CLI MCP Server
- **Purpose**: Secure command execution
- **Features**: Command blocking, output capture
- **Shells**: cmd, powershell, bash

### 3. COM MCP Server (Future)
- **Purpose**: Windows COM automation
- **Use cases**: Outlook integration, startup shortcuts
- **Status**: Available but not yet migrated

## Configuration

MCP servers are configured in `~/.workbuddy/mcp_config.json`:

```json
{
  "servers": {
    "filesystem": {
      "enabled": true,
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "transport": "stdio",
      "env": {
        "FILESYSTEM_ROOT": "C:\\Users"
      }
    },
    "windows-cli": {
      "enabled": true,
      "command": "npx",
      "args": ["-y", "mcp-windows-cli"],
      "transport": "stdio",
      "config": {
        "blockedCommands": ["format", "del /s", "rmdir /s"],
        "blockedPatterns": ["system32", "windows\\system"]
      }
    },
    "com-server": {
      "enabled": false,
      "command": "npx",
      "args": ["-y", "mcp-com-server"],
      "transport": "stdio"
    }
  }
}
```

## Security Benefits

1. **Path Validation**: MCP servers validate all paths before operations
2. **Command Blocking**: Dangerous commands are blocked by default
3. **Process Isolation**: Each MCP server runs in its own process
4. **Configurable Permissions**: Fine-grained control over allowed operations
5. **Audit Trail**: All operations can be logged

## Backward Compatibility

All migrated modules maintain backward compatibility:
- Fallback to direct operations if MCP is unavailable
- Same API surface for calling code
- Graceful degradation of functionality

## Future Enhancements

1. **MCP Directory Watcher**: Real-time file system monitoring
2. **MCP Clipboard Server**: Secure clipboard operations
3. **MCP Audio Server**: Microphone and speaker access
4. **MCP Registry Server**: Windows registry operations
5. **Enhanced COM Server**: Full Office automation

## Testing

To test MCP operations:
```bash
# Run the MCP demo
python demos/mcp_demo.py

# Test file search
python -c "from core.ai_file_search_handler import file_search_handler; print(file_search_handler.natural_language_search('find python files'))"

# Test command execution
python -c "from core.filesearch import run_shell_command; print(run_shell_command('dir', timeout=5))"
```

## Troubleshooting

### MCP Server Not Starting
1. Check if Node.js is installed: `node --version`
2. Verify MCP package installation: `npm list -g @modelcontextprotocol/server-filesystem`
3. Check logs in `~/.workbuddy/mcp_manager.log`

### Fallback to Direct Operations
- This is normal and expected when MCP is unavailable
- Check console output for "MCP not available" messages
- Operations will still work but without MCP security benefits

### Performance Issues
- MCP adds slight overhead vs direct operations
- Everything SDK is still used for high-performance searches when available
- Consider enabling specific MCP servers only when needed

## Summary

The MCP migration enhances WorkBuddy's security and modularity while maintaining full backward compatibility. As new MCP servers become available, WorkBuddy can easily adopt them for additional capabilities. 