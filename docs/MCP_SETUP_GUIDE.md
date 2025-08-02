# MCP Setup Guide for WorkBuddy

This guide will help you set up MCP (Model Context Protocol) servers to enhance WorkBuddy's capabilities.

## Prerequisites

- Node.js installed (for running MCP servers)
- npm (comes with Node.js)
- WorkBuddy installed and working

## Quick Start

### 1. Install Basic MCP Servers

Open a terminal and run:

```bash
# Filesystem MCP Server (already used by WorkBuddy)
npm install -g @modelcontextprotocol/server-filesystem

# Windows CLI Server (for system commands)
npm install -g @simonb97/server-win-cli
```

### 2. Configure WorkBuddy for MCP

The MCP configuration is stored at `~/.workbuddy/mcp_config.json`. 

To enable servers, edit this file:

```json
{
  "servers": {
    "filesystem": {
      "enabled": true,
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", 
              "C:\\Users", "C:\\Projects"],
      "transport": "stdio"
    },
    "windows-cli": {
      "enabled": true,  // Set to true to enable
      "command": "npx",
      "args": ["-y", "@simonb97/server-win-cli"],
      "transport": "stdio"
    }
  }
}
```

### 3. Test MCP Integration

Run the demo script to verify everything works:

```bash
cd workbuddy
python demos/mcp_demo.py
```

## Advanced Setup

### Installing COM MCP Server (for Office Automation)

The COM server allows WorkBuddy to control Office applications:

1. Clone the COM server repository:
   ```bash
   git clone https://github.com/embracethered/mcp-com-server.git
   cd mcp-com-server
   npm install
   npm run build
   ```

2. Update your `mcp_config.json`:
   ```json
   {
     "servers": {
       "com-server": {
         "enabled": true,
         "command": "node",
         "args": ["C:/path/to/mcp-com-server/dist/index.js"],
         "transport": "stdio"
       }
     }
   }
   ```

3. Configure allowed COM objects in the COM server's config for security.

### Creating Custom MCP Servers

You can create custom MCP servers for specific needs:

1. **Clipboard MCP Server** - For clipboard operations
2. **Microphone MCP Server** - Enhanced audio capture
3. **Printer MCP Server** - Controlled printing

Example structure for a custom server:

```javascript
// clipboard-mcp-server.js
const { Server } = require('@modelcontextprotocol/sdk');

const server = new Server({
  name: 'clipboard-server',
  version: '1.0.0'
});

server.setRequestHandler('tools/get_clipboard', async () => {
  // Implementation to get clipboard content
  const content = await getClipboardContent();
  return { content };
});

server.setRequestHandler('tools/set_clipboard', async (params) => {
  // Implementation to set clipboard content
  await setClipboardContent(params.text);
  return { success: true };
});

server.start();
```

## Security Best Practices

1. **Filesystem Server**: Restrict to specific directories
   ```json
   "args": ["-y", "@modelcontextprotocol/server-filesystem", 
            "C:\\Users\\YourName\\Documents", 
            "C:\\Users\\YourName\\Projects"]
   ```

2. **Windows CLI Server**: Configure blocked commands
   - Create a config file for the CLI server
   - Block dangerous commands like `format`, `del`, etc.

3. **COM Server**: Whitelist specific COM objects
   - Only allow necessary applications (Excel, Word, Outlook)
   - Avoid system-critical COM objects

## Integration with WorkBuddy AI

To make the AI aware of MCP tools, update the AI prompt in `core/ai_client.py`:

```python
SYSTEM_PROMPT = """
You have access to the following MCP tools:

1. Filesystem operations:
   - read_file(path): Read file contents
   - list_directory(path): List directory contents
   - write_file(path, content): Write to a file

2. Windows CLI (if enabled):
   - execute_command(command, shell): Run system commands
   
3. Office automation (if COM server enabled):
   - Create and manipulate Office documents
   - Send emails via Outlook
   - Access calendar information

Always ask for user confirmation before:
- Executing system commands
- Writing files
- Sending emails
"""
```

## Troubleshooting

### MCP Server Won't Start

1. Check if Node.js is installed:
   ```bash
   node --version
   npm --version
   ```

2. Verify the server is installed:
   ```bash
   npm list -g @modelcontextprotocol/server-filesystem
   ```

3. Check the logs in `%APPDATA%/WorkBuddy/workbuddy.log`

### Permission Errors

- Run WorkBuddy as administrator (not recommended)
- Or better: Configure MCP servers with appropriate permissions

### COM Server Issues

- Ensure Office is installed
- Check if running as the same user that installed Office
- Verify COM security settings in Windows

## Next Steps

1. Start with basic filesystem operations
2. Enable Windows CLI for system automation
3. Add COM server for Office integration
4. Create custom servers for specific needs
5. Integrate with WorkBuddy's AI for voice-activated automation

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Server Examples](https://github.com/modelcontextprotocol)
- [WorkBuddy MCP Integration Guide](./MCP_INTEGRATION.md) 