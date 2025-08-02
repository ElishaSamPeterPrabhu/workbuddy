"""
MCP Manager for WorkBuddy - Handles Model Context Protocol server connections.

Manages MCP servers for enhanced Windows integration capabilities.
"""

import os
import json
import logging
import subprocess
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
import aiohttp

logger = logging.getLogger(__name__)


class MCPServer:
    """Represents an MCP server instance."""
    
    def __init__(self, name: str, command: str, args: List[str], 
                 transport: str = "stdio"):
        self.name = name
        self.command = command
        self.args = args
        self.transport = transport
        self.process = None
        self.client = None
    
    async def start(self):
        """Start the MCP server process."""
        try:
            if self.transport == "stdio":
                self.process = await asyncio.create_subprocess_exec(
                    self.command,
                    *self.args,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                logger.info(f"Started MCP server: {self.name}")
            elif self.transport == "sse":
                # For SSE transport, servers typically run on HTTP
                self.process = await asyncio.create_subprocess_exec(
                    self.command,
                    *self.args,
                    env={**os.environ, "MCP_TRANSPORT": "sse"}
                )
                await asyncio.sleep(2)  # Give server time to start
                logger.info(f"Started SSE MCP server: {self.name}")
        except Exception as e:
            logger.error(f"Failed to start MCP server {self.name}: {e}")
            raise
    
    async def stop(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            logger.info(f"Stopped MCP server: {self.name}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        if self.transport == "stdio":
            # Send JSON-RPC request via stdin
            request = {
                "jsonrpc": "2.0",
                "method": f"tools/{tool_name}",
                "params": {"arguments": arguments},
                "id": 1
            }
            
            self.process.stdin.write(json.dumps(request).encode() + b'\n')
            await self.process.stdin.drain()
            
            # Read response
            response_line = await self.process.stdout.readline()
            response = json.loads(response_line.decode())
            
            if "error" in response:
                raise Exception(f"MCP error: {response['error']}")
            
            return response.get("result")
        
        elif self.transport == "sse":
            # For SSE, make HTTP request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://localhost:3001/tools/{tool_name}",
                    json=arguments
                ) as resp:
                    return await resp.json()


class MCPManager:
    """Manages MCP server connections for WorkBuddy."""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.config_path = Path.home() / ".workbuddy" / "mcp_config.json"
        self._load_config()
    
    def _load_config(self):
        """Load MCP configuration."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "servers": {
                    "filesystem": {
                        "enabled": True,
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-filesystem", 
                                "C:\\Users", "C:\\Projects"],
                        "transport": "stdio"
                    },
                    "windows-cli": {
                        "enabled": False,  # Disabled by default for security
                        "command": "npx",
                        "args": ["-y", "@simonb97/server-win-cli"],
                        "transport": "stdio"
                    },
                    "com-server": {
                        "enabled": False,  # Requires configuration
                        "command": "node",
                        "args": ["path/to/mcp-com-server/index.js"],
                        "transport": "stdio"
                    }
                }
            }
            self._save_config()
    
    def _save_config(self):
        """Save MCP configuration."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    async def start_server(self, server_name: str):
        """Start a specific MCP server."""
        if server_name not in self.config["servers"]:
            raise ValueError(f"Unknown server: {server_name}")
        
        server_config = self.config["servers"][server_name]
        
        if not server_config.get("enabled", False):
            logger.warning(f"Server {server_name} is disabled")
            return
        
        if server_name in self.servers:
            logger.warning(f"Server {server_name} already running")
            return
        
        server = MCPServer(
            name=server_name,
            command=server_config["command"],
            args=server_config["args"],
            transport=server_config.get("transport", "stdio")
        )
        
        await server.start()
        self.servers[server_name] = server
    
    async def stop_server(self, server_name: str):
        """Stop a specific MCP server."""
        if server_name in self.servers:
            await self.servers[server_name].stop()
            del self.servers[server_name]
    
    async def start_all_enabled(self):
        """Start all enabled MCP servers."""
        for server_name, config in self.config["servers"].items():
            if config.get("enabled", False):
                try:
                    await self.start_server(server_name)
                except Exception as e:
                    logger.error(f"Failed to start {server_name}: {e}")
    
    async def stop_all(self):
        """Stop all running MCP servers."""
        for server_name in list(self.servers.keys()):
            await self.stop_server(server_name)
    
    async def call_tool(self, server_name: str, tool_name: str, 
                       arguments: Dict[str, Any]) -> Any:
        """Call a tool on a specific MCP server."""
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} not running")
        
        return await self.servers[server_name].call_tool(tool_name, arguments)
    
    # Convenience methods for common operations
    
    async def read_file(self, path: str) -> str:
        """Read a file using filesystem MCP server."""
        if "filesystem" not in self.servers:
            await self.start_server("filesystem")
        
        result = await self.call_tool("filesystem", "read_file", {"path": path})
        return result.get("content", "")
    
    async def list_directory(self, path: str) -> List[str]:
        """List directory contents using filesystem MCP server."""
        if "filesystem" not in self.servers:
            await self.start_server("filesystem")
        
        result = await self.call_tool("filesystem", "list_directory", {"path": path})
        return result.get("entries", [])
    
    async def execute_command(self, command: str, shell: str = "powershell") -> str:
        """Execute a command using Windows CLI MCP server."""
        if "windows-cli" not in self.servers:
            logger.warning("Windows CLI server not enabled for security")
            return "Windows CLI server is disabled"
        
        result = await self.call_tool("windows-cli", "execute_command", {
            "command": command,
            "shell": shell
        })
        return result.get("output", "")
    
    async def create_excel_document(self) -> Any:
        """Create a new Excel document using COM MCP server."""
        if "com-server" not in self.servers:
            logger.warning("COM server not enabled")
            return None
        
        # Example of using COM server for Excel
        result = await self.call_tool("com-server", "CreateObject", {
            "progId": "Excel.Application"
        })
        return result


# Global instance
mcp_manager = MCPManager() 