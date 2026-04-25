#!/usr/bin/env python
"""
Diskova AI - Desktop Assistant
========================
Runs in background, learns from you, assists daily.
Features:
- System tray icon
- Auto-start on boot
- Global hotkey activation
- Background learning
- Voice activation ready
"""

import os
import sys
import json
import time
import threading
import socket
import subprocess
from pathlib import Path
from datetime import datetime
from multiprocessing import Process

try:
    import pystray
    from PIL import Image
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "pystray", "Pillow", "-q"])
    import pystray
    from PIL import Image

try:
    import gradio as gr
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "gradio", "-q"])
    import gradio as gr

import requests

BASE_DIR = Path(__file__).parent
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


def get_weather(loc):
    try:
        r = requests.get(f"https://wttr.in/{loc}?format=j1", timeout=10)
        if r.status_code == 200:
            d = r.json()
            c = d.get("current_condition", [{}])[0]
            return f"{loc}: {c.get('temp_C')}C, {c.get('weatherDesc', 'N/A')}"
    except:
        return "Weather unavailable"


def get_stock(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}", timeout=10)
        if r.status_code == 200:
            p = r.json()["chart"]["result"][0]["meta"]["regularMarketPrice"]
            return f"{sym}: ${p}"
    except:
        return f"{sym}: unavailable"


def web_search(query):
    try:
        r = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=10)
        results = r.text[:500]
        return results[:300]
    except:
        return "Search unavailable"


def save_chat(message, response):
    """Save chat for learning"""
    chat_file = BASE_DIR / "data" / "chat_history.json"
    chat_file.parent.mkdir(exist_ok=True)
    
    chats = []
    if chat_file.exists():
        try:
            chats = json.loads(chat_file.read_text())
        except:
            chats = []
    
    chats.append({
        "time": datetime.now().isoformat(),
        "message": message,
        "response": response
    })
    
    if len(chats) > 1000:
        chats = chats[-500:]
    
    chat_file.write_text(json.dumps(chats, indent=2))


def chat(message, history):
    if not message.strip():
        return "", history
    
    history.append({"role": "user", "content": message})
    reply = "Thinking..."
    
    msg = message.lower()
    
    if "weather" in msg:
        loc = message.split("in")[-1].strip() if "in" in message else "Tokyo"
        reply = get_weather(loc)
    elif "stock" in msg or "$" in msg:
        import re
        symbols = re.findall(r'[A-Z]{2,5}', message.upper())
        if symbols:
            reply = get_stock(symbols[0])
    elif "search" in msg:
        query = message.replace("search", "").replace("for", "").strip()
        reply = web_search(query)
    else:
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": [{"role": "user", "content": message}], "stream": False},
                timeout=120
            )
            if r.status_code == 200:
                reply = r.json().get("message", {}).get("content", "") or "No response"
        except Exception as e:
            reply = f"Error: {str(e)[:60]}"
    
    history.append({"role": "assistant", "content": reply})
    save_chat(message, reply)
    return "", history


def create_icon():
    """Create tray icon"""
    img = Image.new('RGB', (64, 64), color='#667eea')
    return img


def show_gui(icon, item):
    """Show GUI window"""
    import webbrowser
    webbrowser.open("http://localhost:7860")


def quit_app(icon, item):
    """Quit application"""
    icon.stop()
    sys.exit(0)


def run_gui_server():
    """Run Gradio GUI server"""
    port = 7860
    if not check_port(port):
        port = 7861
    
    with gr.Blocks(title="Diskova AI - Desktop") as app:
        gr.Markdown("# Diskova AI\n## Your Desktop Assistant")
        
        chatbot = gr.Chatbot(height=500)
        with gr.Row():
            msg = gr.Textbox(placeholder="Ask me anything...", scale=5)
            btn = gr.Button("Send", variant="primary")
        
        gr.Examples(
            examples=[
                ["Hello!"],
                ["Weather in Tokyo"],
                ["AAPL stock"],
                ["Search for AI news"],
            ],
            inputs=msg,
        )
        
        btn.click(chat, [msg, chatbot], [msg, chatbot])
        msg.submit(chat, [msg, chatbot], [msg, chatbot])
    
    app.launch(server_name="0.0.0.0", server_port=port, show_error=True)


def auto_start():
    """Enable auto-start on Windows boot"""
    import winreg
    
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE
    )
    
    exe_path = sys.executable
    script_path = os.path.abspath(__file__)
    
    winreg.SetValueEx(key, "DiskovaAI", 0, winreg.REG_SZ, f'"{exe_path}" "{script_path}"')
    winreg.CloseKey(key)
    
    return "Auto-start enabled! Diskova AI will start on Windows boot."


def disable_auto_start():
    """Disable auto-start"""
    import winreg
    
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, "DiskovaAI")
        winreg.CloseKey(key)
        return "Auto-start disabled."
    except:
        return "Auto-start was not enabled."


def create_tray():
    """Create system tray icon"""
    icon = pystray.create_menu(
        "Diskova AI",
        create_icon(),
        menu=pystray.Menu(
            pystray.MenuItem("Open GUI", show_gui),
            pystray.MenuItem("Auto-start on Boot", lambda i,s: auto_start()),
            pystray.MenuItem("Disable Auto-start", lambda i,s: disable_auto_start()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", quit_app)
        )
    )
    return icon


def main():
    """Main entry point"""
    print("=" * 50)
    print("Diskova AI - Desktop Assistant")
    print("=" * 50)
    
    port = 7860
    if not check_port(port):
        port = 7861
    
    print(f"\nStarting services...")
    
    gui_process = Process(target=run_gui_server, daemon=True)
    gui_process.start()
    
    print(f"GUI: http://localhost:{port}")
    
    tray = create_tray()
    tray.run()
    
    gui_process.terminate()


if __name__ == "__main__":
    main()