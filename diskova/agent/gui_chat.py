#!/usr/bin/env python
"""
Diskova AI - Enhanced Professional GUI
======================================
Enhanced Gradio GUI with modern features.
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

# Import layers
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
    reply = "Thinking..."
    
    try:
        config = get_config()
        
        # Process layers
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
                reply = f"Error: {response.status_code}"
        except Exception as e:
            reply = f"Error: {str(e)[:100]}"
        
        if tool_results:
            tool_info = "\n".join([f"🔧 {t['tool']}: {t['result'][:80]}" for t in tool_results])
            reply = f"{reply}\n\n{tool_info}"
        
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


# Check services
voice_available = False
try:
    vi = VoiceInput()
    voice_available = vi.available
except:
    pass


def create_pro_gui():
    config = get_config()
    port = config.get("gui", {}).get("port", 7860)
    title = config.get("gui", {}).get("title", "Diskova AI")
    
    ollama_url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
    ollama_ok = False
    try:
        ollama_ok = check_service(f"{ollama_url}/api/tags")
    except:
        pass
    
    # Theme with custom CSS
    custom_css = """
    .main-title {
        font-size: 32px !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .status-badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
    }
    .quick-btn {
        transition: all 0.3s ease !important;
    }
    .quick-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    .chat-container {
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
    }
    """
    
    with gr.Blocks(title=title, css=custom_css, theme=gr.themes.Soft()) as app:
        
        # Header with animation
        gr.Markdown("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 20px; margin-bottom: 20px;">
            <h1 class="main-title" style="margin: 0;">🤖 Diskova AI</h1>
            <p style="color: #666; margin: 10px 0 0 0;">Your Intelligent Local Coding Assistant</p>
        </div>
        """)
        
        # Status bar with badges
        status = "🟢 Online" if ollama_ok else "🔴 Offline"
        status_color = "#10b981" if ollama_ok else "#ef4444"
        
        gr.Markdown(f"""
        <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 20px;">
            <span class="status-badge" style="background: {status_color}20; color: {status_color};">
                {status}
            </span>
            <span class="status-badge" style="background: #6c5ce710; color: #6c5ce7;">
                📦 {config.get('model')}
            </span>
            <span class="status-badge" style="background: #00b89410; color: #00b894;">
                🧠 4 Layers Active
            </span>
        </div>
        """)
        
        with gr.Row():
            # Main chat area
            with gr.Column(scale=3):
                gr.Markdown("### ���� Chat")
                chatbot = gr.Chatbot(height=500)
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        show_label=False,
                        placeholder="Type here...",
                        container=True
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Row():
                    gr.Button("🎤 Voice", variant="secondary")
                    gr.Button("🗑️ Clear", variant="stop")
                    gr.Button("📎 Attach File", variant="secondary")
            
            # Sidebar
            with gr.Column(scale=1):
                # Quick Actions with icons
                gr.Markdown("### ⚡ Quick Actions")
                
                with gr.Column():
                    gr.Button("🌐 Web Search", variant="primary", size="sm").click(
                        lambda: "Search for ", outputs=msg_input
                    )
                    gr.Button("🌤️ Weather", size="sm").click(
                        lambda: "What's the weather in ", outputs=msg_input
                    )
                    gr.Button("📅 Calendar", size="sm").click(
                        lambda: "Show calendar ", outputs=msg_input
                    )
                    gr.Button("📝 Reminders", size="sm").click(
                        lambda: "Show reminders ", outputs=msg_input
                    )
                    gr.Button("🖥️ Code", size="sm").click(
                        lambda: "Run ", outputs=msg_input
                    )
                    gr.Button("🌍 Translate", size="sm").click(
                        lambda: "Translate to ", outputs=msg_input
                    )
                    gr.Button("📝 Notes", size="sm").click(
                        lambda: "Show notes ", outputs=msg_input
                    )
                    gr.Button("📈 Stocks", size="sm").click(
                        lambda: "Stock price ", outputs=msg_input
                    )
                
                # Capabilities with visual icons
                gr.Markdown("### ✨ Capabilities")
                gr.Markdown("""
                | Feature | Status |
                |---------|--------|
                | 🔍 Web Search | ✅ |
                | 🌤️ Weather | ✅ |
                | 📈 Stocks | ✅ |
                | 💻 Code Run | ✅ |
                | 📝 Notes | ✅ |
                | 📅 Calendar | ✅ |
                | 📧 Email | ✅ |
                | 🌍 20+ Langs | ✅ |
                """)
                
                # Animated Examples
                gr.Markdown("### 💡 Try Examples")
                gr.Examples(
                    examples=[
                        ["Hello, who are you?"],
                        ["What's the weather in Tokyo?"],
                        ["Search for Python tutorials"],
                        ["Add reminder: Check email at 2pm"],
                        ["Translate 'thank you' to Japanese"],
                        ["Run: print(2+2)"],
                        ["Add note: Meeting ideas"],
                        ["Show my reminders"],
                    ],
                    inputs=msg_input,
                )
        
        # Interactive footer
        gr.Markdown("""
        ---
        <div style="text-align: center; color: #666;">
            🤖 Diskova AI • Powered by Ollama (qwen2.5-coder:1.5b) • 4-Layer AI Architecture
        </div>
        """)
        
        # Event handlers
        submit_btn.click(chat_with_layers, [msg_input, chatbot], [msg_input, chatbot])
        msg_input.submit(chat_with_layers, [msg_input, chatbot], [msg_input, chatbot])
        
        return app, port


def main():
    config = get_config()
    port = config.get("gui", {}).get("port", 7860)
    
    if not check_port(port):
        print(f"Port {port} in use, trying {port + 1}...")
        port = port + 1
    
    app, _ = create_pro_gui()
    print(f"🤖 Diskova AI Pro")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"📦 Model: {config.get('model')}")
    app.launch(server_port=port, server_name="0.0.0.0")


if __name__ == "__main__":
    main()