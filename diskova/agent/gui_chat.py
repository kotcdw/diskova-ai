#!/usr/bin/env python
"""
Diskova AI - Chat Interface
========================
A clean Gradio chat interface.
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
            "title": os.environ.get("GUI_TITLE", "Diskova AI")
        }
    }
    
    if config_path.exists():
        try:
            with open(config_path) as f:
                user_config = json.load(f)
                # Override with env vars
                user_config["model"] = os.environ.get("OLLAMA_MODEL", user_config.get("model"))
                user_config["ollama"]["base_url"] = os.environ.get("OLLAMA_URL", user_config["ollama"]["base_url"])
                user_config["gui"]["port"] = int(os.environ.get("GUI_PORT", str(user_config["gui"]["port"])))
                return user_config
        except:
            return defaults
    return defaults


def chat(message, history):
    if not message:
        return "", history
    
    history.append([message, None])
    
    config = get_config()
    
    if config.get("provider") == "lmstudio":
        url = config.get("lmstudio", {}).get("base_url", "http://localhost:1234/v1")
        model = config.get("lmstudio", {}).get("model") or config.get("model")
        try:
            import requests
            response = requests.post(
                f"{url}/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message}]
                },
                timeout=60
            )
            if response.status_code == 200:
                reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
            else:
                reply = f"LM Studio error: {response.status_code}"
        except Exception as e:
            reply = f"LM Studio not running: {str(e)[:80]}"
    else:
        url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
        model = config.get("model", "qwen2.5-coder:1.5b")
        try:
            import requests
            response = requests.post(
                f"{url}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message}],
                    "stream": False
                },
                timeout=60
            )
            if response.status_code == 200:
                reply = response.json().get("message", {}).get("content", "No response")
            else:
                reply = "Ollama not running. Start with: ollama serve"
        except Exception as e:
            reply = f"Ollama not available: {str(e)[:80]}"
    
    history[-1][1] = reply
    return "", history


def create_gui():
    config = get_config()
    port = config.get("gui", {}).get("port", 7860)
    title = config.get("gui", {}).get("title", "Diskova AI")
    
    # Check services
    ollama_url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
    ollama_ok = check_service(f"{ollama_url}/api/tags")
    
    with gr.Blocks(title=title) as app:
        gr.Markdown(f"# {title}")
        gr.Markdown(f"### Status: {'Online' if ollama_ok else 'Offline'} | Model: {config.get('model')}")
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(height=500)
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        show_label=False,
                        placeholder="Ask me anything...",
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
                    examples=[["Hello"], ["Write hello in Python"]],
                    inputs=msg_input,
                )
        
        submit_btn.click(chat, [msg_input, chatbot], [msg_input, chatbot])
        msg_input.submit(chat, [msg_input, chatbot], [msg_input, chatbot])
    
    return app, port


def main():
    config = get_config()
    port = config.get("gui", {}).get("port", 7860)
    
    # Check port
    if not check_port(port):
        print(f"Port {port} in use, trying {port + 1}...")
        port = port + 1
    
    app, _ = create_gui()
    print(f"Diskova AI - http://localhost:{port}")
    app.launch(
        server_port=port,
        server_name="0.0.0.0",
        show_error=True,
    )

if __name__ == "__main__":
    main()