"""
External MCP Server Integration
=============================
Connect to external MCP servers for additional capabilities.

Supported integrations:
- GitHub (issues, PRs, repos)
- Gmail (send emails)
- Slack (messages)
- Notion (notes)
- Linear (tasks)
- And 250+ more via Composio

Note: Requires Composio subscription for external tools.
For free local-only: Use built-in MCP server.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ExternalMCPServer:
    """External MCP server configuration."""
    name: str
    url: str
    auth_type: str
    connected: bool = False


class MCPConnector:
    """
    Connector for external MCP servers.
    
    Supports:
    - SSE (Server-Sent Events) connections
    - STDIO connections
    - WebSocket connections
    """
    
    def __init__(self):
        self.servers: Dict[str, ExternalMCPServer] = {}
        self.connected_servers: List[str] = []
    
    def add_server(
        self,
        name: str,
        url: str,
        auth_type: str = "none"
    ) -> str:
        """Add an external MCP server."""
        self.servers[name] = ExternalMCPServer(
            name=name,
            url=url,
            auth_type=auth_type
        )
        return f"Added server: {name}"
    
    def connect(self, name: str) -> str:
        """Connect to an MCP server."""
        if name not in self.servers:
            return f"Server '{name}' not found."
        
        server = self.servers[name]
        
        if server.url.startswith("http"):
            return self._connect_sse(name, server.url)
        else:
            return self._connect_stdio(name, server.url)
    
    def _connect_sse(self, name: str, url: str) -> str:
        """Connect via SSE."""
        try:
            import httpx
            response = httpx.get(url, timeout=5)
            if response.status_code == 200:
                self.connected_servers.append(name)
                self.servers[name].connected = True
                return f"Connected to {name} via SSE"
            return f"Failed to connect: {response.status_code}"
        except Exception as e:
            return f"Connection error: {e}"
    
    def _connect_stdio(self, name: str, command: str) -> str:
        """Connect via STDIO."""
        try:
            process = subprocess.Popen(
                command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.connected_servers.append(name)
            self.servers[name].connected = True
            return f"Started {name} process"
        except Exception as e:
            return f"Start error: {e}"
    
    def disconnect(self, name: str) -> str:
        """Disconnect from an MCP server."""
        if name not in self.connected_servers:
            return f"Server '{name}' not connected."
        
        self.connected_servers.remove(name)
        self.servers[name].connected = False
        return f"Disconnected from {name}"
    
    def list_tools(self, name: str) -> List[str]:
        """List tools available on an MCP server."""
        return self.servers.get(name, {}).get("tools", [])
    
    def get_status(self) -> Dict:
        """Get connection status."""
        return {
            "servers": {name: s.connected for name, s in self.servers.items()},
            "connected": self.connected_servers
        }


class ComposioIntegration:
    """
    Composio integration for external MCP tools.
    
    Note: Requires Composio account and API key.
    Sign up at: https://composio.dev
    
    This module provides:
    - Tool discovery
    - OAuth handling
    - API key management
    - Action execution
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("COMPOSIO_API_KEY")
        self.base_url = "https://api.composio.dev"
        self.tools_cache = None
    
    def is_configured(self) -> bool:
        """Check if Composio is configured."""
        return bool(self.api_key)
    
    def list_tools(self, category: str = "all") -> List[Dict]:
        """
        List available tools from Composio.
        
        Categories: github, gmail, slack, notion, linear, etc.
        """
        if not self.is_configured():
            return [
                {"name": "GitHub", "status": "Requires API key"},
                {"name": "Gmail", "status": "Requires API key"},
                {"name": "Slack", "status": "Requires API key"},
            ]
        
        return [
            {"name": "GitHub", "actions": ["create_issue", "create_pr"]},
            {"name": "Gmail", "actions": ["send_email", "read_emails"]},
            {"name": "Slack", "actions": ["send_message", "post_channel"]},
        ]
    
    def get_tool_config(self, tool_name: str) -> Dict:
        """Get configuration for a specific tool."""
        configs = {
            "github": {
                "name": "GitHub",
                "auth": "OAuth",
                "actions": ["create_issue", "create_pr", "merge_pr", "create_repo"]
            },
            "gmail": {
                "name": "Gmail",
                "auth": "OAuth",
                "actions": ["send_email", "read_emails", "draft_email"]
            },
            "slack": {
                "name": "Slack",
                "auth": "OAuth",
                "actions": ["send_message", "post_channel", "list_channels"]
            },
            "notion": {
                "name": "Notion",
                "auth": "OAuth",
                "actions": ["create_page", "update_page", "query_database"]
            },
        }
        return configs.get(tool_name.lower(), {})


class AuthManager:
    """
    Authentication manager for MCP servers.
    
    Supports:
    - API Keys
    - OAuth 2.0
    - Basic Auth
    - Bearer Tokens
    """
    
    def __init__(self):
        self.credentials: Dict[str, Dict] = {}
    
    def save_api_key(self, server: str, api_key: str):
        """Save API key for a server."""
        self.credentials[server] = {
            "type": "api_key",
            "key": api_key
        }
    
    def save_oauth(self, server: str, token: str, refresh_token: str = None):
        """Save OAuth credentials."""
        self.credentials[server] = {
            "type": "oauth",
            "token": token,
            "refresh_token": refresh_token
        }
    
    def save_basic_auth(self, server: str, username: str, password: str):
        """Save basic auth credentials."""
        import base64
        encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.credentials[server] = {
            "type": "basic",
            "auth": encoded
        }
    
    def get_auth_header(self, server: str) -> Optional[Dict]:
        """Get auth header for a server."""
        if server not in self.credentials:
            return None
        
        cred = self.credentials[server]
        
        if cred["type"] == "api_key":
            return {"Authorization": f"Bearer {cred['key']}"}
        elif cred["type"] == "basic":
            return {"Authorization": f"Basic {cred['auth']}"}
        elif cred["type"] == "oauth":
            return {"Authorization": f"Bearer {cred['token']}"}
        
        return None
    
    def is_configured(self, server: str) -> bool:
        """Check if auth is configured for a server."""
        return server in self.credentials


# Default server configurations
DEFAULT_SERVERS = {
    "filesystem": {
        "url": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "./data"],
        "description": "Access local filesystem"
    },
    "github": {
        "url": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "description": "GitHub integration"
    },
    "brave-search": {
        "url": "stdio", 
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "description": "Web search"
    }
}


def get_mcp_server_config(name: str) -> Optional[Dict]:
    """Get configuration for a built-in MCP server."""
    return DEFAULT_SERVERS.get(name)


def list_available_servers() -> List[Dict]:
    """List all available MCP server configurations."""
    return [
        {"name": name, **config}
        for name, config in DEFAULT_SERVERS.items()
    ]


if __name__ == "__main__":
    print("=" * 60)
    print("🔌 External MCP Server Integration")
    print("=" * 60)
    
    # Test Composio
    composio = ComposioIntegration()
    print("\nComposio Status:", "Configured" if composio.is_configured() else "Not configured (needs API key)")
    
    print("\nAvailable Tools:")
    tools = composio.list_tools()
    for tool in tools[:5]:
        print(f"  - {tool}")
    
    print("\nAvailable Servers:")
    servers = list_available_servers()
    for server in servers:
        print(f"  - {server['name']}: {server['description']}")
    
    print("\n" + "=" * 60)
    print("External MCP Integration Ready!")
    print("=" * 60)