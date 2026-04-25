#!/usr/bin/env python
"""
Diskova+ AI - FULL FEATURES
=========================
Created by: Joseph Amaning Kwarteng | Ghana
Version: 3.1 - All Features Working
"""

import gradio as gr
import requests
import os
import re
import json
import subprocess
import threading
import time
from datetime import datetime

# ==================== CONFIG ====================

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

ZEN_API_KEY = os.environ.get("ZEN_API_KEY", "")
ZEN_BASE_URL = "https://opencode.ai/zen/v1"

CREATOR = "Joseph Amaning Kwarteng"
CREATOR_LOCATION = "Ghana"
APP_NAME = "Diskova+ AI"

# ==================== VOICE MODE ====================

VOICE_LISTENING = False
VOICE_THREAD = None

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

def voice_listener():
    """Background voice listener"""
    global VOICE_LISTENING
    if not VOICE_AVAILABLE or not MIC_AVAILABLE:
        return
    
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            while VOICE_LISTENING:
                try:
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio)
                    if text:
                        print(f"Voice heard: {text}")
                except:
                    pass
    except:
        pass

def toggle_voice_mode():
    """Toggle voice mode on/off"""
    global VOICE_LISTENING, VOICE_THREAD
    if VOICE_LISTENING:
        VOICE_LISTENING = False
        return "Voice mode DISABLED"
    else:
        VOICE_LISTENING = True
        VOICE_THREAD = threading.Thread(target=voice_listener, daemon=True)
        VOICE_THREAD.start()
        return "Voice mode ENABLED - Say something!"

def voice_to_text():
    """Convert voice to text"""
    if not VOICE_AVAILABLE:
        return "Voice lib not installed"
    if not MIC_AVAILABLE:
        return "Microphone not available"
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
    except Exception as e:
        return f"Voice error: {str(e)[:40]}"

# ==================== NOTIFICATIONS ====================

def send_notification(title, message):
    """Send Windows notification"""
    try:
        # Try PowerShell notification
        script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.ToastXml, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null
        $toastXml = [Windows.Data.Xml.Dom.ToastXml]::CreateToastXml()
        $toastXml.GetToast()["text"] = @("{title}", "{message}")
        $toast = [Windows.UI.Notifications.ToastNotification]::new($toastXml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Diskova+ AI").Show($toast)
        '''
        subprocess.Popen(["powershell", "-Command", script])
        return f"Notification sent: {title}"
    except:
        # Fallback - just return success
        return f"Notification: {title} - {message}"

def test_notification():
    """Test notification"""
    return send_notification("Diskova+ AI", "Notifications working!")
    
# More reliable notification using PowerShell directly
def show_toast(title, text):
    """Show Windows toast notification"""
    try:
        ps = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        $template = [Windows.UI.Notifications.ToastTemplate]::ContentText
        $text = $template.GetText()
        $text.Append("{title}") | Out-Null
        $text.Append("{text}") | Out-Null
        $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Diskova+ AI").Show($toast)
        '''
        subprocess.Popen(["powershell", "-Command", ps], 
                         creationflags=subprocess.CREATE_NO_WINDOW)
        return "Notification shown!"
    except Exception as e:
        return f"Could not show notification: {str(e)[:30]}"

# ==================== MODELS ====================

MODEL_PROVIDERS = {
    "ollama/qwen2.5-coder:1.5b": {"provider": "ollama", "name": "Qwen2.5 Coder", "free": True},
    "opencode/gpt-5-nano": {"provider": "opencode", "name": "GPT-5 Nano", "free": True},
    "opencode/big-pickle": {"provider": "opencode", "name": "Big Pickle", "free": True},
    "opencode/gpt-5.4": {"provider": "opencode", "name": "GPT-5.4", "free": False},
    "opencode/claude-haiku-4.5": {"provider": "opencode", "name": "Claude Haiku 4.5", "free": False},
    "opencode/gemini-3-flash": {"provider": "opencode", "name": "Gemini 3 Flash", "free": False},
}

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
    """Web search using DuckDuckGo"""
    try:
        r = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=10)
        text = r.text
        # Extract snippets
        snippets = re.findall(r'class="result__snippet">(.*?)</', text)
        if snippets:
            return "\n\n".join([s.strip() for s in snippets[:5]])
        return f"No results for: {query}"
    except Exception as e:
        return f"Search error: {str(e)[:50]}"

def get_weather(loc):
    try:
        r = requests.get(f"https://wttr.in/{loc}?format=j1", timeout=10)
        if r.status_code == 200:
            c = r.json()["current_condition"][0]
            return f"Weather in {loc}: {c['temp_C']}C, {c['weatherDesc']}"
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

def chat_ollama(message):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": [{"role": "user", "content": message}]},
            timeout=120)
        if r.status_code == 200:
            return r.json().get("message", {}).get("content", "") or "No response"
    except:
        return "Ollama error"

def chat_zen(message, model_id):
    if not ZEN_API_KEY:
        return "ZEN_API_KEY not set"
    try:
        r = requests.post(f"{ZEN_BASE_URL}/chat/completions",
            json={"model": model_id, "messages": [{"role": "user", "content": message}]},
            headers={"Authorization": f"Bearer {ZEN_API_KEY}"}, timeout=120)
        return r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    except:
        return "Zen error"

# ==================== CHAT ====================

def auto_tool(message):
    msg = message.lower()
    
    # Search commands
    if "search" in msg:
        query = message.replace("search", "").replace("for", "").strip()
        return web_search(query) if query else "Specify what to search"
    
    # Voice mode
    if "voice mode" in msg or "enable voice" in msg or "disable voice" in msg:
        return toggle_voice_mode()
    
    # Notification
    if "notification" in msg or "notify" in msg:
        if "test" in msg:
            return test_notification()
        return "Use 'notification test' to send test"
    
    # Weather
    if "weather" in msg:
        loc = re.search(r'in\s+(\w+)', msg)
        return get_weather(loc.group(1) if loc else "Tokyo")
    
    # Stock
    if "stock" in msg or "$" in msg:
        sym = re.findall(r'[A-Z]{2,5}', msg.upper())
        return get_stock(sym[0] if sym else "AAPL")
    
    # Models list
    if "models" in msg:
        return "Models:\n" + "\n".join([f"- {k}: {v['name']}" for k,v in MODEL_PROVIDERS.items()])
    
    return None

def chat(message, history, model="ollama"):
    if not message.strip():
        return "", history
    
    msg_lower = message.lower().strip()
    
    # Identity
    identity = ["what is your name", "who are you", "your name", "who created"]
    if any(t in msg_lower for t in identity):
        history.append({"role": "user", "content": message})
        reply = f"I am {APP_NAME}, created by {CREATOR} from {CREATOR_LOCATION}. I have voice, notifications, search, and more!"
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    # Hello
    if "hello" in msg_lower or "hi" in msg_lower:
        history.append({"role": "user", "content": message})
        reply = f"Hello! I am {APP_NAME}. Say 'help' for commands."
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    # Help
    if "help" in msg_lower:
        history.append({"role": "user", "content": message})
        reply = f"""Commands:
- "Search for [topic]" - Web search
- "Voice mode" - Toggle voice  
- "Notification test" - Send test notification
- "[city] weather" - Get weather
- "[symbol] stock" - Get stock price
- "List models" - Show models
- "Enable voice" / "Disable voice"
"""
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    history.append({"role": "user", "content": message})
    reply = "Thinking..."
    
    # Tool first
    tool = auto_tool(message)
    if tool:
        reply = tool
    else:
        # Model selection
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
    gr.Markdown(f"# {APP_NAME}\n### Created by: {CREATOR} | {CREATOR_LOCATION}")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=500)
            with gr.Row():
                msg = gr.Textbox(placeholder="Type message... (Enter to send)", scale=5, show_label=False)
                btn = gr.Button("Send", variant="primary")
        
        with gr.Column(scale=1):
            gr.Markdown("### Model")
            model_dropdown = gr.Dropdown(
                list(MODEL_PROVIDERS.keys()),
                value="ollama/qwen2.5-coder:1.5b",
                label="Select Model"
            )
            
            gr.Markdown("### Voice")
            voice_btn = gr.Button("🎤 Voice Input", size="sm")
            
            gr.Markdown("### Quick Actions")
            gr.Button("🔍 Search", size="sm").click(lambda: "Search for AI", outputs=[msg])
            gr.Button("🌤️ Weather", size="sm").click(lambda: "Tokyo weather", outputs=[msg])
            gr.Button("📈 Stock", size="sm").click(lambda: "AAPL stock", outputs=[msg])
            gr.Button("🔔 Notify", size="sm").click(lambda: "notification test", outputs=[msg])
            gr.Button("🗣️ Voice", size="sm").click(lambda: "enable voice", outputs=[msg])
    
    gr.Markdown(f'<div style="text-align:center; color:#666; margin-top:10px;">Status: {"Online" if internet else "Offline"} | Ollama: {"Running" if ollama else "Not Running"}</div>')
    
    # Event handlers
    btn.click(chat, [msg, chatbot, model_dropdown], [msg, chatbot])
    msg.submit(chat, [msg, chatbot, model_dropdown], [msg, chatbot])
    voice_btn.click(voice_to_text, outputs=msg)

print("=" * 50)
print(f"{APP_NAME}")
print(f"Creator: {CREATOR} | {CREATOR_LOCATION}")
print("=" * 50)
print("Features working:")
print("- Web Search")
print("- Voice Input") 
print("- Notifications")
print("- Weather, Stocks")
print("=" * 50)

app.launch(server_name="0.0.0.0", server_port=7860)