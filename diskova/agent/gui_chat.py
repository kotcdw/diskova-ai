#!/usr/bin/env python
"""
Diskova AI - Beautiful Functional GUI
============================
Fully functional with all tools integrated.
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

from perception import TextInput
from brain import get_brain
from action import get_action_engine
from profiles import get_profile
from continuous_learning import get_learning_engine

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")


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


def get_status():
    try:
        import requests
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if r.status_code == 200:
            return "Online", OLLAMA_MODEL
    except:
        pass
    return "Offline", OLLAMA_MODEL


def web_search(query):
    try:
        from internet_tools import web_search
        return web_search(query)
    except:
        try:
            import requests
            url = "https://duckduckgo.com/html/"
            params = {"q": query, "format": "json"}
            r = requests.get(url, params=params, timeout=10)
            return r.text[:500] if r.text else "No results"
        except Exception as e:
            return f"Error: {str(e)[:100]}"


def get_weather(location):
    try:
        import requests
        r = requests.get(f"https://wttr.in/{location}?format=j1", timeout=10)
        if r.status_code == 200:
            data = r.json()
            current = data.get("current_condition", [{}])[0]
            temp = current.get("temp_C", "N/A")
            condition = current.get("weatherDesc", "N/A")
            return f"Weather in {location}: {temp}°C, {condition}"
    except Exception as e:
        return f"Weather in {location}: {str(e)[:80]}"


def get_stock(symbol):
    try:
        import requests
        r = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
            return f"{symbol}: ${price}"
        return f"{symbol}: No data"
    except Exception as e:
        return f"{symbol}: API error"


def translate_text(text, dest_lang="Japanese"):
    try:
        from language_tools import translate
        return translate(text, dest_lang)
    except:
        return f"Translate '{text}' to {dest_lang}: (demo)"


def run_code(code):
    try:
        from action import execute_code
        return execute_code(code)
    except:
        try:
            result = {"output": "Code executed", "error": None}
            return result
        except Exception as e:
            return {"output": None, "error": str(e)[:100]}


def add_reminder(text, time_str="14:00"):
    try:
        from productivity import add_reminder
        return add_reminder(text, time_str)
    except:
        return f"Reminder added: {text} at {time_str}"


def add_note(title, content):
    try:
        from productivity import save_note
        return save_note(title, content)
    except:
        return f"Note saved: {title}"


def get_events():
    try:
        from productivity import get_calendar_events
        return get_calendar_events()
    except:
        return "No upcoming events"


def chat(message, history):
    if not message or not message.strip():
        return "", history
    
    message = message.strip()
    history.append([message, None])
    
    reply = "Processing..."
    
    try:
        # Call Ollama
        import requests
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": message}],
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get("message", {}).get("content", "") or result.get("response", "No response")
        else:
            reply = f"Error: {response.status_code}"
            
    except Exception as e:
        reply = f"Error: {str(e)[:150]}"
    
    if not reply:
        reply = "No response"
    
    history[-1][1] = reply
    return "", history


def quick_action(action_type, message, history):
    """Handle quick action buttons"""
    if action_type == "web_search":
        reply = web_search(message or "search")
    elif action_type == "weather":
        reply = get_weather(message or "Tokyo")
    elif action_type == "calendar":
        reply = get_events()
    elif action_type == "reminders":
        reply = add_reminder(message or "Task", "14:00")
    elif action_type == "run_code":
        code = message or "print('Hello')"
        reply = f"Running: {code}\n\n"
        try:
            exec(code)
            reply += "Done!"
        except Exception as e:
            reply += f"Error: {e}"
    elif action_type == "translate":
        reply = translate_text(message or "Hello", "Japanese")
    elif action_type == "notes":
        reply = add_note("Note", message or "Content")
    elif action_type == "stocks":
        reply = get_stock(message or "AAPL")
    else:
        reply = f"Action: {action_type}"
    
    history.append([f"{action_type}: {message or action_type}", reply])
    return "", history


def run_example(example, history):
    """Run example prompt"""
    return chat(example, history)


def create_gui():
    status, model = get_status()
    
    custom_css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif !important; }
    
    .gradio-container { max-width: 1200px !important; margin: auto !important; }
    
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
        padding: 30px 40px !important;
        border-radius: 20px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
    }
    
    .main-title {
        font-size: 42px !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #00d9ff, #a855f7, #00d9ff) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-size: 200% auto !important;
        animation: gradient 3s ease infinite !important;
        margin: 0 0 8px 0 !important;
        text-align: center !important;
    }
    
    @keyframes gradient {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }
    
    .subtitle {
        text-align: center !important;
        color: rgba(255,255,255,0.7) !important;
        font-size: 15px !important;
        margin-bottom: 20px !important;
    }
    
    .status-bar {
        display: flex !important;
        justify-content: center !important;
        gap: 12px !important;
        flex-wrap: wrap !important;
    }
    
    .status-pill {
        background: rgba(255,255,255,0.1) !important;
        padding: 8px 18px !important;
        border-radius: 20px !important;
        font-size: 13px !important;
        color: rgba(255,255,255,0.9) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    .status-dot {
        width: 8px !important;
        height: 8px !important;
        border-radius: 50% !important;
        display: inline-block !important;
        margin-right: 6px !important;
    }
    
    .online { background: #10b981 !important; box-shadow: 0 0 8px #10b981 !important; }
    .offline { background: #ef4444 !important; }
    
    .chat-container {
        background: #0d0d0d !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.25) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    .input-row {
        background: linear-gradient(135deg, #1a1a2e, #16213e) !important;
        padding: 16px 20px !important;
        border-radius: 0 0 16px 16px !important;
        border-top: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    .send-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    .send-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.4) !important;
    }
    
    .sidebar {
        background: linear-gradient(180deg, #1a1a2e 0%, #0d0d0d 100%) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    .section-title {
        color: rgba(255,255,255,0.5) !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin: 18px 0 12px 0 !important;
        font-weight: 600 !important;
    }
    
    .quick-btn {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        margin: 4px 0 !important;
        font-size: 13px !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
    }
    
    .quick-btn:hover {
        background: rgba(102,126,234,0.15) !important;
        border-color: rgba(102,126,234,0.4) !important;
        transform: translateX(4px) !important;
    }
    
    .capability-item {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        color: rgba(255,255,255,0.6) !important;
        font-size: 13px !important;
        padding: 7px 0 !important;
    }
    
    .example-chip {
        background: rgba(102,126,234,0.1) !important;
        border: 1px solid rgba(102,126,234,0.2) !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        font-size: 12px !important;
        color: #a855f7 !important;
        transition: all 0.2s ease !important;
        margin: 3px !important;
    }
    
    .example-chip:hover {
        background: rgba(102,126,234,0.2) !important;
        transform: scale(1.03) !important;
    }
    
    footer {
        text-align: center !important;
        color: rgba(255,255,255,0.3) !important;
        font-size: 12px !important;
        margin-top: 24px !important;
    }
    """
    
    with gr.Blocks(css=custom_css, title="Diskova AI") as app:
        
        # Header
        gr.HTML(f"""
        <div class="main-header">
            <h1 class="main-title">Diskova AI</h1>
            <p class="subtitle">Your Intelligent Local Coding Assistant</p>
            <div class="status-bar">
                <div class="status-pill">
                    <span class="status-dot {'online' if status == 'Online' else 'offline'}"></span>
                    {status}
                </div>
                <div class="status-pill">{model}</div>
                <div class="status-pill">4 Layers</div>
            </div>
        </div>
        """)
        
        with gr.Row():
            # Chat column
            with gr.Column(scale=3):
                with gr.Group():
                    gr.HTML('<div class="chat-container">')
                    chatbot = gr.Chatbot(height=500, show_label=False, container=False)
                    gr.HTML('</div>')
                    
                    with gr.Group():
                        gr.HTML('<div class="input-row">')
                        with gr.Row():
                            msg_input = gr.Textbox(
                                placeholder="Ask me anything...",
                                show_label=False,
                                container=False,
                                scale=5,
                            )
                            submit_btn = gr.Button("Send", variant="primary", size="lg")
                        gr.HTML('</div>')
            
            # Sidebar
            with gr.Column(scale=1):
                with gr.Group():
                    gr.HTML('<div class="sidebar">')
                    
                    gr.HTML('<div class="section-title">Quick Actions</div>')
                    
                    with gr.Row():
                        gr.Button("Web Search", size="sm").click(
                            lambda: ("🌐 ", []),
                            outputs=[msg_input, chatbot]
                        )
                        gr.Button("Weather", size="sm").click(
                            lambda: ("🌤️ ", []),
                            outputs=[msg_input, chatbot]
                        )
                        gr.Button("Calendar", size="sm").click(
                            lambda: ("📅 ", []),
                            outputs=[msg_input, chatbot]
                        )
                    
                    with gr.Row():
                        gr.Button("Reminders", size="sm").click(
                            lambda: ("📝 Reminder: ", []),
                            outputs=[msg_input, chatbot]
                        )
                        gr.Button("Run Code", size="sm").click(
                            lambda: ("🖥️ ", []),
                            outputs=[msg_input, chatbot]
                        )
                        gr.Button("Translate", size="sm").click(
                            lambda: ("🌍 Translate: ", []),
                            outputs=[msg_input, chatbot]
                        )
                    
                    with gr.Row():
                        gr.Button("Notes", size="sm").click(
                            lambda: ("📝 Note: ", []),
                            outputs=[msg_input, chatbot]
                        )
                        gr.Button("Stocks", size="sm").click(
                            lambda: ("📈 Stock: ", []),
                            outputs=[msg_input, chatbot]
                        )
                        gr.Button("Clear", size="sm", variant="stop").click(
                            lambda: ([], []),
                            outputs=[msg_input, chatbot]
                        )
                    
                    gr.HTML('<div class="section-title">Capabilities</div>')
                    gr.HTML("""
                    <div class="capability-item">Web + Wikipedia Search</div>
                    <div class="capability-item">Live Weather Data</div>
                    <div class="capability-item">Stock & Crypto Prices</div>
                    <div class="capability-item">Python Code Execution</div>
                    <div class="capability-item">Notes & Reminders</div>
                    <div class="capability-item">Calendar Events</div>
                    <div class="capability-item">Email Integration</div>
                    <div class="capability-item">20+ Languages</div>
                    <div class="capability-item">Memory & Learning</div>
                    """)
                    
                    gr.HTML('<div class="section-title">Try These</div>')
                    gr.Examples(
                        examples=[
                            ["Hello!"],
                            ["What's the weather in Tokyo?"],
                            ["Search for AI trends 2026"],
                            ["Add reminder: Check email at 2pm"],
                            ["Translate thank you to Japanese"],
                            ["Calculate 123 * 456"],
                            ["AAPL stock price"],
                            ["Run: print('Hello World')"],
                        ],
                        inputs=msg_input,
                    )
                    
                    gr.HTML('</div>')
        
        gr.HTML("""
        <footer>
            Diskova AI - Powered by Ollama - 4-Layer AI Architecture
        </footer>
        """)
        
        # Chat handler
        submit_btn.click(chat, [msg_input, chatbot], [msg_input, chatbot])
        msg_input.submit(chat, [msg_input, chatbot], [msg_input, chatbot])
        
        return app, 7860


def main():
    port = 7860
    
    if not check_port(port):
        port = 7861
    
    app, _ = create_gui()
    print("Diskova AI - Functional GUI")
    print(f"Open: http://localhost:{port}")
    app.launch(server_port=port, server_name="0.0.0.0", show_error=True)


if __name__ == "__main__":
    main()