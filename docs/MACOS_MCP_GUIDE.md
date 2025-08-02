# macOS MCP Configuration Guide for WorkBuddy

Since you're running WorkBuddy on macOS, the Windows-specific MCP servers won't work. However, the architecture is designed with fallbacks, so WorkBuddy functions normally. Here's how to optimize it for macOS.

## Current Status

✅ **Working with Fallbacks:**
- File operations fall back to direct access
- Command execution uses subprocess
- Storage uses SQLite directly
- Search uses basic file system walk

## Recommended macOS MCP Servers

### 1. Filesystem Server (Cross-platform)
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

Update `~/.workbuddy/mcp_config.json`:
```json
{
  "servers": {
    "filesystem": {
      "enabled": true,
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "transport": "stdio",
      "env": {
        "FILESYSTEM_ROOT": "/Users"
      }
    }
  }
}
```

### 2. GitHub Server
```bash
npm install -g @modelcontextprotocol/server-github
```

Add to config:
```json
"github": {
  "enabled": true,
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "transport": "stdio",
  "env": {
    "GITHUB_TOKEN": "your-github-token"
  }
}
```

### 3. SQLite Server
```bash
npm install -g @modelcontextprotocol/server-sqlite
```

Add to config:
```json
"sqlite": {
  "enabled": true,
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sqlite", "~/.workbuddy/workbuddy.db"],
  "transport": "stdio"
}
```

### 4. Brave Search Server
```bash
npm install -g @modelcontextprotocol/server-brave-search
```

Add to config:
```json
"brave-search": {
  "enabled": true,
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "transport": "stdio",
  "env": {
    "BRAVE_API_KEY": "your-brave-api-key"
  }
}
```

## macOS-Specific Enhancements

### Future MCP Servers for macOS
- **Spotlight MCP**: Native macOS search integration
- **AppleScript MCP**: macOS automation
- **Homebrew MCP**: Package management
- **Terminal MCP**: iTerm2/Terminal.app integration

### Current Workarounds
1. **File Search**: Uses basic file walk (slower but functional)
2. **Commands**: Direct subprocess execution (secure on macOS)
3. **Outlook**: Use web-based Outlook instead of COM automation

## Testing on macOS

Run the macOS-specific test:
```bash
python3 tests/test_mcp_migration_mac.py
```

This verifies all fallback mechanisms work correctly.

## Benefits of the MCP Architecture

Even without Windows-specific servers:
1. **Future-ready**: Easy to add macOS MCP servers
2. **Security-minded**: Code is structured for sandboxed operations
3. **Modular**: Clean separation of concerns
4. **Cross-platform**: Same codebase works on Windows/Mac/Linux

## Example: Using Filesystem MCP on macOS

Once installed, the filesystem MCP server provides:
- Sandboxed file access (restricted to allowed paths)
- Async operations for better performance
- Standardized error handling

WorkBuddy will automatically detect and use it when available. 