# MCP Integration for WorkBuddy

Model Context Protocol (MCP) servers provide a standardized way to integrate with Windows system resources, offering significant advantages over direct API calls.

## What is MCP?

MCP is an open protocol that standardizes how AI applications interface with external tools and data sources. Think of it as a "USB-C port for AI applications" - a universal interface that allows any MCP-enabled AI to connect with any MCP server.

## Benefits for WorkBuddy

### 1. **Enhanced Security**
- MCP servers run as separate processes with controlled permissions
- Path validation and command blocking built into servers
- No direct system access from the AI process
- Centralized security policies

### 2. **Better Modularity**
- Each capability is a separate server (filesystem, CLI, COM, etc.)
- Easy to add/remove features without changing core code
- Servers can be updated independently
- Community-driven ecosystem of servers

### 3. **Simplified Development**
- No need to handle low-level Windows APIs
- Standardized interface for all operations
- Automatic error handling and data formatting
- Focus on AI logic rather than system integration

### 4. **Cross-Platform Potential**
- Same AI code works on Windows, Linux, Mac
- Only server implementations change per platform
- Future-proof architecture

## Available MCP Servers for Windows

### 1. **Filesystem MCP Server**
- Safe file operations with path restrictions
- Already integrated into WorkBuddy's file search
- Handles reading, writing, listing files

### 2. **Windows CLI MCP Server**
Provides secure command execution:
```python
# Execute PowerShell commands safely
result = await mcp_manager.execute_command(
    "Get-Process | Where-Object {$_.CPU -gt 100}",
    shell="powershell"
)
```

### 3. **COM MCP Server**
Automate Windows applications:
```python
# Create Excel document and manipulate it
excel = await mcp_manager.call_tool("com-server", "CreateObject", {
    "progId": "Excel.Application"
})

# Add data to Excel
await mcp_manager.call_tool("com-server", "SetProperty", {
    "object": excel,
    "property": "Visible",
    "value": True
})
```

### 4. **Potential Future Servers**
- **Microphone MCP**: Enhanced audio capture
- **Printer MCP**: Controlled printing operations
- **Clipboard MCP**: Secure clipboard access
- **Registry MCP**: Safe registry operations

## Enhanced Jarvis Features with MCP

### Morning Briefing 2.0
```python
# Use COM server to check Outlook calendar
outlook = await mcp_manager.call_tool("com-server", "CreateObject", {
    "progId": "Outlook.Application"
})

# Get today's appointments directly from Outlook
appointments = await mcp_manager.call_tool("com-server", "InvokeMethod", {
    "object": outlook,
    "method": "GetTodayAppointments"
})
```

### Voice-Activated System Control
```python
# User: "Jarvis, close all Chrome windows"
await mcp_manager.execute_command(
    "Get-Process chrome | Stop-Process",
    shell="powershell"
)

# User: "Create a spreadsheet with my tasks"
excel = await create_excel_with_tasks()
```

### Smart File Management
```python
# Use filesystem MCP for safe operations
files = await mcp_manager.list_directory("C:/Users/Documents")
for file in files:
    if file.endswith(".tmp"):
        await mcp_manager.call_tool("filesystem", "delete_file", {
            "path": file
        })
```

## Security Configuration

MCP servers can be configured with strict security policies:

```json
{
  "servers": {
    "windows-cli": {
      "enabled": true,
      "config": {
        "blockedCommands": ["format", "del", "rm"],
        "allowedPaths": ["C:/Users/YourName/Documents"],
        "maxCommandLength": 1000,
        "commandTimeout": 30
      }
    }
  }
}
```

## Implementation Plan

### Phase 1: Core MCP Infrastructure ✓
- [x] Create MCP Manager
- [x] Basic server lifecycle management
- [x] Filesystem server integration

### Phase 2: Enhanced Capabilities
- [ ] Integrate Windows CLI server for system commands
- [ ] Add COM server for Office automation
- [ ] Create custom clipboard MCP server
- [ ] Build microphone MCP server for better audio

### Phase 3: AI Integration
- [ ] Update AI prompts to use MCP tools
- [ ] Add MCP tool discovery to AI context
- [ ] Create unified command interface
- [ ] Implement safety confirmations

### Phase 4: Advanced Features
- [ ] Multi-server orchestration
- [ ] Server health monitoring
- [ ] Performance optimization
- [ ] Custom WorkBuddy MCP servers

## Example: Complete Office Automation

```python
async def create_meeting_summary():
    """Create a Word document with meeting notes from audio."""
    
    # 1. Capture audio using future Microphone MCP
    audio = await mcp_manager.call_tool("microphone", "record_audio", {
        "duration": 300  # 5 minutes
    })
    
    # 2. Transcribe using existing speech recognition
    transcript = await transcribe_audio(audio)
    
    # 3. Create Word document using COM MCP
    word = await mcp_manager.call_tool("com-server", "CreateObject", {
        "progId": "Word.Application"
    })
    
    doc = await mcp_manager.call_tool("com-server", "InvokeMethod", {
        "object": word,
        "method": "Documents.Add"
    })
    
    # 4. Add content
    await mcp_manager.call_tool("com-server", "InvokeMethod", {
        "object": doc,
        "method": "Content.InsertAfter",
        "args": [f"Meeting Summary\n\n{transcript}"]
    })
    
    # 5. Save document
    await mcp_manager.call_tool("com-server", "InvokeMethod", {
        "object": doc,
        "method": "SaveAs",
        "args": ["C:/Users/Documents/meeting_summary.docx"]
    })
```

## Comparison: Direct API vs MCP

### Traditional Approach (Current)
```python
# Direct Windows API calls
import win32com.client
import os

# Need to handle COM directly
word = win32com.client.Dispatch("Word.Application")
doc = word.Documents.Add()
# Error handling, security, etc. all manual
```

### MCP Approach (Proposed)
```python
# Standardized MCP interface
word = await mcp_manager.call_tool("com-server", "CreateObject", {
    "progId": "Word.Application"
})
# Security, error handling, logging all built-in
```

## Getting Started

1. **Install MCP servers**:
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   npm install -g @simonb97/server-win-cli
   ```

2. **Configure WorkBuddy**:
   ```python
   # In main.py, add MCP initialization
   from core.mcp_manager import mcp_manager
   
   async def init_mcp():
       await mcp_manager.start_all_enabled()
   ```

3. **Use in AI responses**:
   ```python
   # AI can now use MCP tools
   files = await mcp_manager.list_directory("C:/Documents")
   ```

## Conclusion

MCP servers provide a powerful, secure, and standardized way to enhance WorkBuddy's capabilities. By adopting MCP, we can:

- Make WorkBuddy more secure (sandboxed operations)
- Add new features easily (just add new servers)
- Improve cross-platform compatibility
- Leverage the growing MCP ecosystem
- Focus on AI intelligence rather than system integration

The investment in MCP integration will pay dividends as the ecosystem grows and more servers become available. 