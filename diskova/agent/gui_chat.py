#!/usr/bin/env python
"""
Diskova AI - Complete AI Assistant GUI
==============================
Gradio GUI for Diskova AI with professional layout.
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

from perception import TextInput, VoiceInput, ImageInput
from brain import Brain, get_brain
from action import ActionEngine, get_action_engine
from response import OutputHandler, get_output_handler
from profiles import get_profile
from continuous_learning import get_learning_engine
from knowledge_base import get_knowledge_base


def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            s.close()
            return True
        except:
            return False


def check_service(url):
    try:
        import requests
        r = requests.get(url, timeout=2)
        return r.status_code == 200
    except:
        return False


def get_config():
    config_path = BASE_DIR.parent / "config" / "llm_config.json"
    defaults = {
        "provider": "ollama",
        "model": os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b"),
        "ollama": {
            "base_url": os.environ.get("OLLAMA_URL", "http://localhost:11434"),
            "model": os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
        },
        "gui": {"port": 7860, "title": "Diskova AI"}
    }
    if config_path.exists():
        try:
            with open(config_path) as f:
                user_config = json.load(f)
                user_config["model"] = os.environ.get("OLLAMA_MODEL", user_config.get("model"))
                user_config["ollama"]["base_url"] = os.environ.get("OLLAMA_URL", user_config["ollama"]["base_url"])
                return user_config
        except:
            return defaults
    return defaults


def chat_with_layers(message, history):
    if not message or not message.strip():
        return "", history
    
    message = message.strip()
    history.append([message, None])
    reply = "Processing..."
    
    try:
        config = get_config()
        
        text_input = TextInput()
        brain = get_brain()
        action_engine = get_action_engine()
        
        brain_processed = brain.process(message)
        intent = brain_processed.get("parsed", {}).get("intents", ["general"])[0]
        
        tool_calls = action_engine.determine_tool_use(intent, message)
        tool_results = []
        if tool_calls:
            tool_results = action_engine.execute_tools(tool_calls)
        
        llm_messages = brain.generate_prompt()
        llm_messages.append({"role": "user", "content": message})
        
        url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
        model = config.get("model", "qwen2.5-coder:1.5b")
        
        try:
            import requests
            response = requests.post(
                f"{url}/api/chat",
                json={"model": model, "messages": llm_messages, "stream": False},
                timeout=120
            )
            if response.status_code == 200:
                result = response.json()
                reply = result.get("message", {}).get("content", "") or result.get("response", "No response")
            else:
                reply = f"Ollama: {response.status_code}"
        except Exception as e:
            reply = f"Error: {str(e)[:100]}"
        
        if tool_results:
            tool_info = "\n".join([f"Tool: {t['tool']} -> {t['result'][:100]}" for t in tool_results])
            reply = f"{reply}\n\n---\n{tool_info}"
        
        brain.short_memory.add("assistant", reply)
        
        profile = get_profile("default")
        profile.add_query(message)
        
        learning = get_learning_engine()
        learning.feedback.add(message, reply, 5)
        
    except Exception as e:
        reply = f"Error: {str(e)[:100]}"
    
    if not reply:
        reply = "No response"
    
    history[-1][1] = reply
    return "", history


voice_available = False
try:
    vi = VoiceInput()
    voice_available = vi.available
except:
    pass


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
    
    with gr.Blocks(title=title, theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 15px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0; font-size: 36px;">🤖 Diskova AI</h1>
            <p style="color: #e0e0e0; margin: 5px 0 0 0;">Your Local AI Coding Assistant</p>
        </div>
        """)
        
        status_emoji = "🟢" if ollama_ok else "🔴"
        gr.Markdown(f"""
        <div style="display: flex; justify-content: space-between; padding: 15px; background: #f8f9fa; border-radius: 10px; margin-bottom: 20px;">
            <span><b>Status:</b> {status_emoji} {'Online' if ollama_ok else 'Offline'}</span>
            <span><b>Model:</b> {config.get('model')}</span>
            <span><b>Layers:</b> 4 Active ✓</span>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 💬 Chat")
                chatbot = gr.Chatbot(height=450)
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        show_label=False, 
                        placeholder="Type your message here...",
                        container=True,
                        scale=4
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Row():
                    if voice_available:
                        gr.Button("🎤 Voice")
                    gr.Button("🗑️ Clear")
            
            with gr.Column(scale=1):
                gr.Markdown("### ⚡ Quick Actions")
                gr.Button("🌐 Web Search", variant="primary")
                gr.Button("🌤️ Get Weather")
                gr.Button("📅 Show Calendar")
                gr.Button("�Show Reminders")  
                gr.Button("🖥️ Run Code")
                gr.Button("🌍 Translate")
                gr.Button("�Show Notes")
                gr.Button("�Get Stock Prices")
                
                gr.Markdown("### ��� Capabilities")
                gr.Markdown("""
                <table style="width:100%;">
                <tr><td>🔍 Search</td><td>Web + Wikipedia</td></tr>
                <tr><td>🌤️ Weather</td><td>Live data</td></tr>
                <tr><td>�Stocks</td><td>Crypto/Forex</td></tr>
                <tr><td>💻 Code</td><td>Python/JS</td></tr>
                <tr><td>�Notes</td><td>Create/Read</td></tr>
                <tr><td>�Calendar</td><td>Events</td></tr>
                <tr><td>�Email</td><td>Send/Receive</td></tr>
                <tr><td>🌍 Languages</td><td>20+</td></tr>
                </table>
                """)
                
                gr.Markdown("### 💡 Try These")
                gr.Examples(
                    examples=[
                        ["Hello!"],
                        ["What's the weather in Tokyo?"],
                        ["Search for AI trends 2026"],
                        ["Add reminder: Check email at 2pm"],
                        ["Translate thank you to Japanese"],
                        ["Calculate 123 * 456"],
                        ["Run: print('Hello')"],
                    ],
                    inputs=msg_input,
                )
        
        submit_btn.click(chat_with_layers, [msg_input, chatbot], [msg_input, chatbot])
        msg_input.submit(chat_with_layers, [msg_input, chatbot], [msg_input, chatbot])
        
        gr.Markdown("---")
        gr.Markdown("*Powered by Ollama (qwen2.5-coder:1.5b) | 4-Layer AI Architecture*")
        
        return app, port


def main():
    config = get_config()
    port = config.get("gui", {}).get("port", 7860)
    
    if not check_port(port):
        print(f"Port {port} in use, trying {port + 1}...")
        port = port + 1
    
    app, _ = create_gui()
    print(f"Diskova AI")
    print(f"URL: http://localhost:{port}")
    print(f"Model: {config.get('model')}")
    app.launch(server_port=port, server_name="0.0.0.0", show_error=True)


if __name__ == "__main__":
    main()