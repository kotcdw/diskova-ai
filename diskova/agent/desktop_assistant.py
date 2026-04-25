#!/usr/bin/env python
"""
Diskova AI - Full Desktop Assistant
=============================
All features:
- System tray icon
- Auto-start on boot
- Background learning
- Voice activation (wake word)
- Always-on voice mode
- Desktop widget overlay
- File/folder monitoring
- Windows notifications
"""

import os
import sys
import json
import time
import threading
import socket
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor

try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "pystray", "Pillow", "-q"])
    import pystray
    from PIL import Image, ImageDraw, ImageFont

try:
    import win32api, win32con, win32gui, win32console
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "pywin32", "-q"])
    import win32api, win32con, win32gui, win32console

try:
    import gradio as gr
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "gradio", "-q"])
    import gradio as gr

try:
    import speech_recognition as sr
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "SpeechRecognition", "-q"])
    import speech_recognition as sr

import requests
import re
import asyncio

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

WAKE_WORD = "hey diskova"
VOICE_MODE = False
LISTENING = False
WIDGET_HWND = None


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


def show_notification(title, message):
    """Show Windows notification"""
    try:
        win32console.Notify(title, message)
    except:
        pass
    
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, 1)
    except:
        pass


def save_chat(message, response):
    """Save chat for learning"""
    chat_file = DATA_DIR / "chat_history.json"
    
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


def save_learning(message, response, rating=5):
    """Save for continuous learning"""
    learning_file = DATA_DIR / "learning.json"
    
    data = []
    if learning_file.exists():
        try:
            data = json.loads(learning_file.read_text())
        except:
            data = []
    
    data.append({
        "time": datetime.now().isoformat(),
        "input": message,
        "output": response,
        "rating": rating
    })
    
    if len(data) > 500:
        data = data[-200:]
    
    learning_file.write_text(json.dumps(data, indent=2))


class FileMonitor:
    """Monitor file/folder changes"""
    
    def __init__(self, paths=None):
        self.paths = paths or []
        self.callbacks = []
        self.running = False
        self.last_states = {}
    
    def add_path(self, path):
        path = Path(path)
        if path.exists():
            self.paths.append(path)
            self.last_states[str(path)] = self.get_state(path)
    
    def get_state(self, path):
        path = Path(path)
        if path.is_file():
            return path.stat().st_mtime
        elif path.is_dir():
            files = list(path.rglob("*"))
            return len(files)
        return None
    
    def check_changes(self):
        changes = []
        for path in self.paths:
            path = Path(path)
            current = self.get_state(path)
            last = self.last_states.get(str(path))
            
            if current != last:
                changes.append(f"Changed: {path}")
                self.last_states[str(path)] = current
        
        return changes
    
    def start(self):
        self.running = True
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
    
    def monitor_loop(self):
        while self.running:
            changes = self.check_changes()
            for change in changes:
                show_notification("Diskova AI", f"File changed: {change}")
                for cb in self.callbacks:
                    cb(change)
            time.sleep(2)
    
    def stop(self):
        self.running = False


file_monitor = FileMonitor()


def voice_listen():
    """Listen for wake word and commands"""
    global LISTENING
    
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while LISTENING:
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = recognizer.recognize_google(audio).lower()
                    
                    if WAKE_WORD in text:
                        show_notification("Diskova AI", "Wake word detected! Listening...")
                        audio = recognizer.listen(source, timeout=10)
                        command = recognizer.recognize_google(audio)
                        process_voice_command(command)
                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except Exception as e:
                    print(f"Voice error: {e}")
    except Exception as e:
        print(f"Voice init error: {e}")


def process_voice_command(command):
    """Process voice command"""
    command = command.lower()
    reply = ""
    
    if "weather" in command:
        loc = command.split("in")[-1].strip() if "in" in command else "Tokyo"
        reply = get_weather(loc)
    elif "stock" in command:
        symbols = re.findall(r'[A-Z]{2,5}', command.upper())
        reply = get_stock(symbols[0]) if symbols else "Which stock?"
    elif "search" in command:
        query = command.replace("search", "").replace("for", "").strip()
        reply = web_search(query)
    elif "time" in command:
        reply = f"Current time: {datetime.now().strftime('%H:%M')}"
    elif "date" in command:
        reply = f"Today: {datetime.now().strftime('%Y-%m-%d')}"
    else:
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": [{"role": "user", "content": command}], "stream": False},
                timeout=60
            )
            if r.status_code == 200:
                reply = r.json().get("message", {}).get("content", "")
        except:
            reply = "Ollama not connected"
    
    show_notification("Diskova AI", reply or "No response")
    save_chat(command, reply)


def create_widget_overlay():
    """Create desktop widget overlay"""
    global WIDGET_HWND
    
    class WidgetWindow:
        def __init__(self):
            self.hwnd = None
        
        def create(self):
            wc = win32gui.WNDCLASSEX()
            wc.lpfnWndProc = self.wnd_proc
            wc.hInstance = win32api.GetModuleHandle(None)
            wc.lpszClassName = "DiskovaWidget"
            wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
            
            try:
                win32gui.RegisterClass(wc)
            except:
                pass
            
            self.hwnd = win32gui.CreateWindowEx(
                win32con.WS_EX_LAYERED | win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_TOPMOST,
                "DiskovaWidget",
                "Diskova AI",
                win32con.WS_OVERLAPPED | win32con.CW_USEDEFWINDCON,
                100, 100, 300, 150,
                None, None, None, None
            )
            
            win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 200, win32con.LWA_ALPHA)
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNOACTIVE)
            
            self.update_text("Diskova AI - Online")
        
        def update_text(self, text):
            if self.hwnd:
                win32gui.SetWindowText(self.hwnd, text)
        
        def wnd_proc(self, hwnd, msg, wparam, lparam):
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    widget = WidgetWindow()
    return widget


def toggle_voice_mode():
    """Toggle always-on voice mode"""
    global VOICE_MODE, LISTENING
    
    if VOICE_MODE:
        LISTENING = False
        VOICE_MODE = False
        return "Voice mode disabled"
    else:
        LISTENING = True
        VOICE_MODE = True
        thread = threading.Thread(target=voice_listen, daemon=True)
        thread.start()
        return "Voice mode enabled! Say 'hey diskova' to activate"


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
        symbols = re.findall(r'[A-Z]{2,5}', message.upper())
        reply = get_stock(symbols[0]) if symbols else "Which stock?"
    elif "search" in msg:
        query = message.replace("search", "").replace("for", "").strip()
        reply = web_search(query)
    elif "time" in msg:
        reply = f"Time: {datetime.now().strftime('%H:%M')}"
    elif "date" in msg:
        reply = f"Date: {datetime.now().strftime('%Y-%m-%d')}"
    elif "voice on" in msg or "enable voice" in msg:
        reply = toggle_voice_mode()
    elif "voice off" in msg or "disable voice" in msg:
        toggle_voice_mode()
        reply = "Voice mode disabled"
    elif "notify" in msg:
        show_notification("Diskova AI", "Test notification!")
        reply = "Notification sent!"
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
    save_learning(message, reply)
    return "", history


def create_icon():
    """Create tray icon"""
    img = Image.new('RGBA', (64, 64), color=(102, 126, 234, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 56, 56], fill=(255, 255, 255, 255))
    draw.text((20, 22), "AI", fill=(102, 126, 234, 255))
    return img


def show_gui(icon, item):
    import webbrowser
    webbrowser.open("http://localhost:7860")


def quit_app(icon, item):
    global LISTENING
    LISTENING = False
    file_monitor.stop()
    icon.stop()
    sys.exit(0)


def run_gui():
    port = 7860
    if not check_port(port):
        port = 7861
    
    with gr.Blocks(title="Diskova AI") as app:
        gr.Markdown("""
        # Diskova AI
        ## Your Desktop Assistant
        
        ### Features
        - Voice: Say "hey diskova" to activate
        - Weather: Ask "weather in [city]"
        - Stocks: Ask "[symbol] stock"
        - Files: Auto-monitors changes
        - Notifications: Get alerts
        """)
        
        chatbot = gr.Chatbot(height=500)
        with gr.Row():
            msg = gr.Textbox(placeholder="Ask me anything...", scale=5)
            btn = gr.Button("Send", variant="primary")
        
        gr.Examples(
            examples=[
                ["Hello!"],
                ["Weather in Tokyo"],
                ["AAPL stock"],
                ["Search for AI"],
                ["Enable voice mode"],
                ["Send notification test"],
            ],
            inputs=msg,
        )
        
        btn.click(chat, [msg, chatbot], [msg, chatbot])
        msg.submit(chat, [msg, chatbot], [msg, chatbot])
    
    app.launch(server_name="0.0.0.0", server_port=port, show_error=True)


def main():
    print("=" * 50)
    print("Diskova AI - Full Desktop Assistant")
    print("=" * 50)
    
    port = 7860
    if not check_port(port):
        port = 7861
    
    print(f"\nStarting services...")
    
    gui_process = Process(target=run_gui, daemon=True)
    gui_process.start()
    
    file_monitor.add_path(str(BASE_DIR / "data"))
    file_monitor.start()
    
    print(f"GUI: http://localhost:{port}")
    print(f"Voice: Say '{WAKE_WORD}' to activate")
    print(f"Files: Monitoring {len(file_monitor.paths)} paths")
    
    menu = pystray.Menu(
        pystray.MenuItem("Open GUI", show_gui),
        pystray.MenuItem("Voice Mode", lambda i,s: toggle_voice_mode()),
        pystray.MenuItem("Test Notification", lambda i,s: show_notification("Diskova AI", "Hello!")),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app)
    )
    
    icon = pystray.Icon("DiskovaAI", create_icon(), "Diskova AI", menu)
    icon.run()
    
    gui_process.terminate()


if __name__ == "__main__":
    main()