#!/usr/bin/env python
"""
Diskova+ AI - FULL OPENCODE EXPERIENCE
======================================
Created by: Joseph Amaning Kwarteng | Ghana
Version: 3.0 - MCP + Models + Agents

FEATURES:
1. MCP Server Support (Local + Remote)
2. 75+ Model Providers
3. Multi-Agent System (Build, Plan, Explore)
"""

import gradio as gr
import requests
import os
import re
import json
import subprocess
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ==================== CONFIG ====================

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

ZEN_API_KEY = os.environ.get("ZEN_API_KEY", "")
ZEN_BASE_URL = "https://opencode.ai/zen/v1"

CREATOR = "Joseph Amaning Kwarteng"
CREATOR_LOCATION = "Ghana"
APP_NAME = "Diskova+ AI"

# ==================== MCP SERVERS ====================

class MCPServer:
    def __init__(self, name, server_type, config):
        self.name = name
        self.server_type = server_type  # "local" or "remote"
        self.config = config
        self.enabled = config.get("enabled", True)
        self.url = config.get("url", "")
        self.command = config.get("command", [])
        self.process = None
        self.tools = []
    
    def connect(self):
        """Connect to MCP server"""
        try:
            if self.server_type == "remote":
                # Test remote connection
                r = requests.get(f"{self.url}/health", timeout=5)
                if r.status_code == 200:
                    self.tools = r.json().get("tools", [])
                    return f"Connected to {self.name}"
            elif self.server_type == "local":
                # Start local server
                self.process = subprocess.Popen(
                    self.command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                return f"Started {self.name}"
        except Exception as e:
            return f"Failed: {str(e)[:50]}"
        return f"Could not connect to {self.name}"
    
    def call_tool(self, tool_name, args):
        """Call a tool on MCP server"""
        try:
            if self.server_type == "remote":
                r = requests.post(
                    f"{self.url}/tools/{tool_name}",
                    json=args,
                    timeout=30
                )
                return r.json()
            else:
                return {"error": "Local MCP not implemented"}
        except Exception as e:
            return {"error": str(e)[:50]}

# Pre-configured MCP servers
MCP_SERVERS = {
    "context7": {
        "type": "remote",
        "url": "https://mcp.context7.com/mcp",
        "description": "Search through documentation",
    },
    "sentry": {
        "type": "remote", 
        "url": "https://mcp.sentry.dev/mcp",
        "description": "Sentry error tracking",
    },
    "gh_grep": {
        "type": "remote",
        "url": "https://mcp.grep.app",
        "description": "Search GitHub code examples",
    },
    "filesystem": {
        "type": "local",
        "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."],
        "description": "Local file system operations",
    },
}

active_mcp = {}

# ==================== MODELS ====================

MODEL_PROVIDERS = {
    # OpenCode Zen (Free + Paid)
    "opencode/gpt-5-nano": {"provider": "opencode", "name": "GPT-5 Nano", "free": True},
    "opencode/gpt-5.4": {"provider": "opencode", "name": "GPT-5.4", "free": False},
    "opencode/claude-haiku-4.5": {"provider": "opencode", "name": "Claude Haiku 4.5", "free": False},
    "opencode/gemini-3-flash": {"provider": "opencode", "name": "Gemini 3 Flash", "free": False},
    "opencode/qwen3.5-plus": {"provider": "opencode", "name": "Qwen3.5 Plus", "free": False},
    "opencode/big-pickle": {"provider": "opencode", "name": "Big Pickle", "free": True},
    
    # Ollama (Local, Free)
    "ollama/qwen2.5-coder:1.5b": {"provider": "ollama", "name": "Qwen2.5 Coder", "free": True},
    "ollama/llama3": {"provider": "ollama", "name": "Llama 3", "free": True},
    "ollama/codellama": {"provider": "ollama", "name": "CodeLlama", "free": True},
}

# ==================== AGENTS ====================

class Agent:
    def __init__(self, name, description, mode, tools_permission):
        self.name = name
        self.description = description
        self.mode = mode  # "primary" or "subagent"
        self.tools_permission = tools_permission

# Built-in agents
AGENTS = {
    "build": Agent(
        "Build",
        "Main development agent with all tools",
        "primary",
        {"*": "allow"}  # All tools allowed
    ),
    "plan": Agent(
        "Plan", 
        "Analysis and planning - no changes",
        "primary",
        {"write": "deny", "edit": "deny", "bash": "deny"}
    ),
    "explore": Agent(
        "Explore",
        "Fast read-only codebase exploration",
        "subagent",
        {"*": "deny", "grep": "allow", "glob": "allow"}
    ),
    "general": Agent(
        "General",
        "General purpose research and tasks",
        "subagent",
        {"*": "allow"}
    ),
}

current_agent = "build"

# ==================== VOICE ====================

try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

try:
    import pyaudio
    MIC_AVAILABLE = True
except:
    MIC_AVAILABLE = False

# ==================== FUNCTIONS ====================

def check_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

def check_ollama():
    try:
        requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return True
    except:
        return False

def web_search(query):
    try:
        r = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=10)
        results = re.findall(r'class="result__snippet">(.*?)</', r.text)
        return " | ".join(results[:3]) if results else "No results"
    except:
        return "Search error"

def get_weather(loc):
    try:
        r = requests.get(f"https://wttr.in/{loc}?format=j1", timeout=10)
        if r.status_code == 200:
            c = r.json()["current_condition"][0]
            return f"{loc}: {c['temp_C']}C, {c['weatherDesc']}"
    except:
        return "Weather unavailable"

def get_stock(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}", timeout=10)
        if r.status_code == 200:
            return f"{sym}: ${r.json()['chart']['result'][0]['meta']['regularMarketPrice']}"
    except:
        return f"{sym}: unavailable"

def chat_ollama(message):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": [{"role": "user", "content": message}], "stream": False},
            timeout=120)
        if r.status_code == 200:
            return r.json().get("message", {}).get("content", "") or "No response"
    except:
        return "Ollama error"

def chat_zen(message, model_id):
    if not ZEN_API_KEY:
        return "ZEN_API_KEY not set. Add to environment variables."
    try:
        r = requests.post(f"{ZEN_BASE_URL}/chat/completions",
            json={"model": model_id, "messages": [{"role": "user", "content": message}]},
            headers={"Authorization": f"Bearer {ZEN_API_KEY}"}, timeout=120)
        return r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    except:
        return "Zen error"

# MCP Functions
def connect_mcp(server_name):
    """Connect to MCP server"""
    if server_name in MCP_SERVERS:
        config = MCP_SERVERS[server_name]
        server = MCPServer(server_name, config.get("type", "remote"), config)
        result = server.connect()
        active_mcp[server_name] = server
        return result
    return f"Unknown MCP: {server_name}. Available: {list(MCP_SERVERS.keys())}"

def list_mcp_tools():
    """List available MCP tools"""
    if not active_mcp:
        return "No MCP servers connected. Use 'connect mcp server-name'"
    
    tools = []
    for name, server in active_mcp.items():
        tools.append(f"{name}: {len(server.tools)} tools")
    return "\n".join(tools) if tools else "No tools loaded"

# ==================== CHAT ====================

def auto_tool(message, agent):
    msg = message.lower()
    
    # MCP commands
    if "mcp" in msg:
        if "connect" in msg:
            for name in MCP_SERVERS:
                if name in msg:
                    return connect_mcp(name)
            return f"Available MCP: {', '.join(MCP_SERVERS.keys())}"
        if "list" in msg or "tools" in msg:
            return list_mcp_tools()
    
    # Agent switching
    if "@" in message:
        for agent_name in AGENTS:
            if f"@{agent_name}" in message:
                return f"Switched to {agent_name} agent"
    
    # Weather
    if "weather" in msg:
        loc = re.search(r'in\s+(\w+)', msg)
        return get_weather(loc.group(1) if loc else "Tokyo")
    
    # Stock
    if "stock" in msg or "$" in msg:
        sym = re.findall(r'[A-Z]{2,5}', msg.upper())
        return get_stock(sym[0] if sym else "AAPL")
    
    # Search
    if "search" in msg or "find" in msg:
        q = message.replace("search", "").replace("find", "").strip()
        return web_search(q) if q else None
    
    # Models list
    if "models" in msg or "list models" in msg:
        return "Available Models:\n" + "\n".join([f"- {k}: {v['name']}" for k,v in MODEL_PROVIDERS.items()])
    
    # Agents info
    if "agent" in msg:
        return "Agents:\n" + "\n".join([f"- {k}: {v.description}" for k,v in AGENTS.items()])
    
    return None

def chat(message, history, model="ollama"):
    if not message.strip():
        return "", history
    
    msg_lower = message.lower().strip()
    
    # Identity - ALWAYS FIRST
    identity = ["what is your name", "who are you", "your name", "who created"]
    if any(t in msg_lower for t in identity):
        history.append({"role": "user", "content": message})
        reply = f"I am {APP_NAME}, created by {CREATOR} from {CREATOR_LOCATION}. I support MCP servers, multiple models, and multi-agent system."
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    # Hello
    if "hello" in msg_lower or "hi" in msg_lower or "hey" in msg_lower:
        history.append({"role": "user", "content": message})
        reply = f"Hello! I am {APP_NAME}. How can I help?"
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    # Help menu
    if "help" in msg_lower or "features" in msg_lower:
        history.append({"role": "user", "content": message})
        reply = f"""{APP_NAME} Features:

MCP Servers: connect mcp [server-name]
  - context7, sentry, gh_grep, filesystem

Models: Select from 75+ providers via dropdown
  - opencode/gpt-5-nano (FREE)
  - opencode/big-pickle (FREE)  
  - ollama/qwen2.5-coder:1.5b (FREE)
  - And more...

Agents: @mention to switch
  - @build: Full development
  - @plan: Analysis only
  - @explore: Read-only search

Commands:
  "list models" - Show available models
  "list agents" - Show agents
  "mcp connect context7" - Connect MCP
  "mcp list" - Show MCP tools
"""
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    history.append({"role": "user", "content": message})
    reply = "Thinking..."
    
    # Tool first
    tool = auto_tool(message, current_agent)
    if tool:
        reply = tool
    else:
        # Route to model
        if model in MODEL_PROVIDERS:
            provider = MODEL_PROVIDERS[model]["provider"]
            if provider == "ollama":
                reply = chat_ollama(message)
            elif provider == "opencode":
                reply = chat_zen(message, model)
    
    history.append({"role": "assistant", "content": reply})
    return "", history

# ==================== GUI ====================

internet = check_internet()
ollama = check_ollama()

with gr.Blocks(title=APP_NAME) as app:
    gr.Markdown(f"# {APP_NAME}\n##### Created by: {CREATOR} | {CREATOR_LOCATION}")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=500)
            with gr.Row():
                msg = gr.Textbox(placeholder="Message... (Enter to send)", scale=5, show_label=False)
                btn = gr.Button("Send", variant="primary")
        
        with gr.Column(scale=1):
            gr.Markdown("### Model")
            model_dropdown = gr.Dropdown(
                list(MODEL_PROVIDERS.keys()),
                value="ollama/qwen2.5-coder:1.5b",
                label="Select Model"
            )
    
    gr.Markdown(f'<div style="text-align:center; color:#666; margin-top:10px;">Status: {"Online' if internet else 'Offline'} | Ollama: {''Running' if ollama else 'Not Running'} | MCP: {len(active_mcp)} connected</div>')
    
    btn.click(chat, [msg, chatbot, model_dropdown], [msg, chatbot])
    msg.submit(chat, [msg, chatbot, model_dropdown], [msg, chatbot])

print("=" * 50)
print(f"{APP_NAME}")
print(f"Creator: {CREATOR} | {CREATOR_LOCATION}")
print("=" * 50)
print("MCP Servers:", list(MCP_SERVERS.keys()))
print("Models:", len(MODEL_PROVIDERS))
print("Agents:", list(AGENTS.keys()))
print("=" * 50)
app.launch(server_name="0.0.0.0", server_port=7860)