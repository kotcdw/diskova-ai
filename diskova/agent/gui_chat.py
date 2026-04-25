#!/usr/bin/env python
"""
Diskova AI - Complete AI Assistant
================================
A full implementation of modern AI assistant architecture.

Layers:
- Perception: Text input, Voice (STT), Image (CV)
- Brain: NLP, Reasoning, Memory
- Action: Tool calling
- Response: Output formatting
"""

import os
import sys
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import socket

try:
    import gradio as gr
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "gradio", "-q"])
    import gradio as gr
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "gradio", "-q"])
    import gradio as gr

# Import layers
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Import our layers
from perception import TextInput, VoiceInput, ImageInput
from brain import Brain, get_brain
from action import ActionEngine, get_action_engine
from response import OutputHandler, get_output_handler

# Import additional features
from profiles import UserProfile, get_profile
from continuous_learning import LearningEngine, get_learning_engine
from knowledge_base import KnowledgeBase, get_knowledge_base

# Voice input state
voice_input = VoiceInput()
voice_available = voice_input.available


def process_voice(audio_path, history):
    """Process voice input and return text."""
    if not audio_path:
        return "", history
    
    try:
        from perception import VoiceInput
        vi = VoiceInput()
        if vi.available:
            # Note:audio_path is the recorded audio file
            # Use speech_recognition if available
            text = vi.listen(timeout=5)
            if text:
                history.append([f"[Voice]: {text}", None])
                return text, history
    except Exception as e:
        history.append(["[Voice]", f"Error: {str(e)[:50]}"])
    
    return "", history


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


def chat_with_layers(message, history):
    """Chat using all AI assistant layers."""
    if not message or not message.strip():
        return "", history
    
    message = message.strip()
    history.append([message, None])
    
    config = get_config()
    reply = "Processing..."
    tool_results = []
    
    try:
        # 1. PERCEPTION LAYER - Process input
        text_input = TextInput()
        perception_result = text_input.process(message)
        
        # 2. BRAIN LAYER - Process with NLP and Memory
        brain = get_brain()
        brain_processed = brain.process(message)
        intent = brain_processed.get("parsed", {}).get("intents", ["general"])[0]
        
        # 3. ACTION LAYER - Determine tool usage
        action_engine = get_action_engine()
        tool_calls = action_engine.determine_tool_use(intent, message)
        
        # Execute tools if needed
        if tool_calls:
            tool_results = action_engine.execute_tools(tool_calls)
        
        # 4. Build prompt for LLM
        llm_messages = brain.generate_prompt()
        llm_messages.append({
            "role": "user",
            "content": message
        })
        
        # 5. Call LLM (Ollama)
        if config.get("provider") == "lmstudio":
            url = config.get("lmstudio", {}).get("base_url", "http://localhost:1234/v1")
            model = config.get("lmstudio", {}).get("model") or config.get("model")
            try:
                import requests
                response = requests.post(
                    f"{url}/chat/completions",
                    json={"model": model, "messages": llm_messages},
                    timeout=120
                )
                if response.status_code == 200:
                    reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
                else:
                    reply = f"LM Studio error: {response.status_code}"
            except Exception as e:
                reply = f"LM Studio: {str(e)[:80]}"
        else:
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
                    reply = result.get("message", {}).get("content", "")
                    if not reply:
                        reply = result.get("response", "No response")
                else:
                    reply = f"Ollama: {response.status_code}"
            except Exception as e:
                reply = f"Error: {str(e)[:100]}"
        
        # 6. RESPONSE LAYER - Format output
        if tool_results:
            tool_info = "\n".join([f"Tool: {t['tool']} -> {t['result'][:100]}" for t in tool_results])
            reply = f"{reply}\n\n---\n{tool_info}"
        
        # Add to brain memory
        brain.short_memory.add("assistant", reply)
        
        # Track user profile
        profile = get_profile("default")
        profile.add_query(message)
        
        # Learn from feedback
        learning = get_learning_engine()
        learning.feedback.add(message, reply, 5)  # Default rating
        
    except Exception as e:
        reply = f"Error: {str(e)[:100]}"
    
    if not reply:
        reply = "No response"
    
    history[-1][1] = reply
    return "", history


# Check MCP mode
MCP_SERVER = os.environ.get("GRADIO_MCP_SERVER", "false").lower() == "true"


def create_gui():
    config = get_config()
    port = config.get("gui", {}).get("port", 7860)
    title = config.get("gui", {}).get("title", "Diskova AI")
    
    # Check services
    ollama_url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
    ollama_ok = False
    try:
        ollama_ok = check_service(f"{ollama_url}/api/tags")
    except:
        pass
    
    with gr.Blocks(title=title) as app:
        gr.Markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0;">🤖 Diskova AI</h1>
            <p style="color: #e0e0e0; margin: 5px 0 0 0;">Your Local AI Coding Assistant</p>
        </div>
        """)
        
        status_color = "🟢 Online" if ollama_ok else "🔴 Offline"
        gr.Markdown(f"""
        **Status:** {status_color} | **Model:** {config.get('model')}
        
**Architecture:**
        - 🔤 Perception (Input) ✓
        - 🧠 Brain (NLP + Memory) ✓
        - 🔧 Action (Tools) ✓
        - 📝 Response (Output) ✓
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                gr.Markdown("### 💬 Chat")
                chatbot = gr.Chatbot(height=500)
                
                msg_input = gr.Textbox(
                    show_label=False, 
                    placeholder="Type your message here... (Press Enter)",
                    container=True
                )
                submit_btn = gr.Button("📤 Send", variant="primary")
                
                with gr.Row():
                    voice_btn = gr.Button("🎤 Voice", variant="secondary")
                    clear_btn = gr.Button("🗑️ Clear", variant="stop")
            
            with gr.Column(scale=1):
                gr.Markdown("### ⚡ Quick Actions")
                gr.Button("🌐 Web Search", variant="primary")
                gr.Button("🌤️ Weather")
                gr.Button("📅 Calendar")
                gr.Button("📝 Reminders")
                gr.Button("🖥️ Run Code")
                gr.Button("🌍 Translate")
                gr.Button("📝 Notes")
                gr.Button("📈 Stocks")
                
                gr.Markdown("### ✨ Capabilities")
                gr.Markdown(f"""
- **🔍 Search**: Web + Wikipedia
- **🌤️ Weather**: Live weather
- **📈 Stocks**: Crypto/Forex
- **💻 Code**: Run Python/JS
- **📝 Productivity**: Notes, Reminders
- **📅 Calendar**: Events + ICS
- **📧 Email**: Send/Receive
- **🌍 Languages**: 20+ Translation
- **💾 Memory**: Session + Knowledge
- **🎤 Voice**: Speech input
                """)
                
                gr.Markdown("### 💡 Examples")
                gr.Examples(
                    examples=[
                        ["Hello!"],
                        ["What's the weather in Tokyo?"],
                        ["Search for AI trends 2026"],
                        ["Add reminder: Check email at 2pm"],
                        ["Translate thank you to Japanese"],
                        ["Calculate 123 * 456"],
                        ["Add note: Project ideas - Phase 1"],
                        ["Run: print('Hello World')"],
                    ],
                    inputs=msg_input,
                )
        
        # Event handlers
        clear_btn.click(lambda: ("", []), outputs=[msg_input, chatbot])
        submit_btn.click(chat_with_layers, [msg_input, chatbot], [msg_input, chatbot])
        msg_input.submit(chat_with_layers, [msg_input, chatbot], [msg_input, chatbot])
        
        # Footer
        gr.Markdown("""
        ---
        *Diskova AI - Built with 4-Layer AI Architecture*
        *Powered by Ollama (qwen2.5-coder:1.5b)*
        """)
        
        return app, port


def main():
    config = get_config()
    port = config.get("gui", {}).get("port", 7860)
    
    if not check_port(port):
        print(f"Port {port} in use, trying {port + 1}...")
        port = port + 1
    
    app, _ = create_gui()
    print(f"Diskova AI - Full Architecture")
    print(f"URL: http://localhost:{port}")
    print(f"Model: {config.get('model')}")
    app.launch(server_port=port, server_name="0.0.0.0", show_error=True)


if __name__ == "__main__":
    main()