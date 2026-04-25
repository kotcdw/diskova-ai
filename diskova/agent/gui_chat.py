#!/usr/bin/env python
"""
Diskova AI - Chat Interface with MCP Server
=====================================
A clean Gradio chat interface that also serves MCP tools.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import socket

try:
    import gradio as gr
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "gradio", "-q"])
    import gradio as gr

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

current_model = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")


def check_port(port):
    """Check if port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            s.close()
            return True
        except:
            return False


def check_service(url):
    """Check if service is accessible."""
    try:
        import requests
        r = requests.get(url, timeout=2)
        return r.status_code == 200
    except:
        return False


def get_config():
    """Load config with env variable fallbacks."""
    config_path = BASE_DIR.parent / "config" / "llm_config.json"
    
    defaults = {
        "provider": "ollama",
        "model": os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b"),
        "ollama": {
            "base_url": os.environ.get("OLLAMA_URL", "http://localhost:11434"),
            "model": os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
        },
        "gui": {
            "port": int(os.environ.get("GUI_PORT", "7860")),
            "title": "Diskova AI"
        }
    }
    
    if config_path.exists():
        try:
            with open(config_path) as f:
                user_config = json.load(f)
                user_config["model"] = os.environ.get("OLLAMA_MODEL", user_config.get("model"))
                user_config["ollama"]["base_url"] = os.environ.get("OLLAMA_URL", user_config["ollama"]["base_url"])
                user_config["gui"]["port"] = int(os.environ.get("GUI_PORT", str(user_config["gui"]["port"])))
                return user_config
        except Exception as e:
            print(f"Config error: {e}")
            return defaults
    return defaults


# MCP Tools
def search_knowledge(query: str, category: str = "all") -> str:
    """Search your knowledge base."""
    return f"Searched '{query}' in {category} - No results yet. Add knowledge to knowledge/ folder."


def get_code_snippet(language: str, snippet_type: str = "hello") -> str:
    """Get a code snippet."""
    snippets = {
        "python": {"hello": "print('Hello, World!')"},
        "javascript": {"hello": "console.log('Hello, World!');"},
        "go": {"hello": 'fmt.Println("Hello, World!")'},
    }
    return snippets.get(language, {}).get(snippet_type, "# Not found")


def create_project(template: str, project_name: str) -> str:
    """Create a new project from template."""
    return f"Would create {template} project: {project_name}"


def analyze_project(path: str = ".") -> str:
    """Analyze project structure."""
    return "Project analysis: No data yet"


# Chat function
def chat(message, history):
    if not message or not message.strip():
        return "", history
    
    message = message.strip()
    history.append([message, None])
    config = get_config()
    reply = "Starting up..."
    
    try:
        if config.get("provider") == "lmstudio":
            url = config.get("lmstudio", {}).get("base_url", "http://localhost:1234/v1")
            model = config.get("lmstudio", {}).get("model") or config.get("model")
            try:
                import requests
                response = requests.post(
                    f"{url}/chat/completions",
                    json={"model": model, "messages": [{"role": "user", "content": message}]},
                    timeout=120
                )
                if response.status_code == 200:
                    reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
                else:
                    reply = f"LM Studio error: {response.status_code} - {response.text[:100]}"
            except Exception as e:
                reply = f"LM Studio not available: {str(e)[:100]}"
        else:
            url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
            model = config.get("model", "qwen2.5-coder:1.5b")
            try:
                import requests
                response = requests.post(
                    f"{url}/api/chat",
                    json={"model": model, "messages": [{"role": "user", "content": message}], "stream": False},
                    timeout=120
                )
                if response.status_code == 200:
                    result = response.json()
                    reply = result.get("message", {}).get("content", "")
                    if not reply:
                        reply = result.get("response", "No response")
                else:
                    reply = f"Ollama error: {response.status_code}"
            except requests.exceptions.ConnectionError:
                reply = "Cannot connect to Ollama. Is Ollama running? Start with: ollama serve"
            except Exception as e:
                reply = f"Error: {str(e)[:100]}"
    except Exception as e:
        reply = f"Error: {str(e)[:100]}"
    
    if not reply:
        reply = "No response from model"
    
    history[-1][1] = reply
    return "", history


# Check if MCP server mode
MCP_SERVER = os.environ.get("GRADIO_MCP_SERVER", "false").lower() == "true"


def create_gui():
    config = get_config()
    port = config.get("gui", {}).get("port", 7860)
    title = config.get("gui", {}).get("title", "Diskova AI")
    
    ollama_url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
    ollama_ok = False
    try:
        ollama_ok = check_service(f"{ollama_url}/api/tags")
    except:
        pass
    
    # Expose MCP tools if enabled
    tools = []
    if MCP_SERVER:
        from gradio.tools import Tool
        tools = [
            Tool(name="search_knowledge", fn=search_knowledge, description="Search knowledge base"),
            Tool(name="get_code_snippet", fn=get_code_snippet, description="Get code snippet"),
            Tool(name="create_project", fn=create_project, description="Create project"),
            Tool(name="analyze_project", fn=analyze_project, description="Analyze project"),
        ]
    
    with gr.Blocks(title=title, tools=tools if tools else None) as app:
        gr.Markdown(f"# {title}")
        gr.Markdown(f"### Status: {'Online' if ollama_ok else 'Offline - Start Ollama with: ollama serve'} | Model: {config.get('model')} | MCP: {MCP_SERVER}")
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    height=500,
                    show_copy_button=True,
                    likeable=True,
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        show_label=False, 
                        placeholder="Ask me anything... (Press Enter to send)",
                        scale=4, 
                        container=True
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
            
            with gr.Column(scale=1):
                gr.Markdown("### Quick Actions")
                gr.Button("Clear Chat", variant="secondary").click(
                    lambda: (None, []), 
                    outputs=[msg_input, chatbot]
                )
                gr.Markdown("### Examples")
                gr.Examples(
                    examples=[
                        ["Hello, how are you?"],
                        ["Write a hello world in Python"],
                        ["Explain what is an API"],
                    ],
                    inputs=msg_input,
                )
        
        # Event handlers
        submit_btn.click(chat, [msg_input, chatbot], [msg_input, chatbot])
        msg_input.submit(chat, [msg_input, chatbot], [msg_input, chatbot])
        
        # Clear input on submit
        def clear_input():
            return ""
        
    return app, port


def main():
    config = get_config()
    port = config.get("gui", {}).get("port", 7860)
    
    if not check_port(port):
        print(f"Port {port} in use, trying {port + 1}...")
        port = port + 1
    
    app, _ = create_gui()
    print(f"Diskova AI - http://localhost:{port}")
    print(f"Model: {config.get('model')}")
    if MCP_SERVER:
        print(f"MCP Server enabled - Use with Claude Desktop")
    app.launch(server_port=port, server_name="0.0.0.0", show_error=True, mcp_server=MCP_SERVER)


if __name__ == "__main__":
    main()