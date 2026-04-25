#!/usr/bin/env python
"""
Diskova+ AI - Clean IDE
==================
Created by: Joseph Amaning Kwarteng | Ghana
Version: 2.1 - Clean Minimal IDE

A clean, professional AI coding assistant like OpenCode.
"""

import gradio as gr
import requests
import os
import re
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

# ==================== PROVIDERS ====================

PROVIDERS = {
    "ollama": {"name": "Ollama", "model": "qwen2.5-coder:1.5b"},
    "gpt-5-nano": {"name": "GPT-5 Nano", "model": "opencode/gpt-5-nano"},
    "claude-haiku": {"name": "Claude Haiku", "model": "opencode/claude-haiku-4-5"},
}

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
        text = r.text
        results = re.findall(r'class="result__snippet">(.*?)</', text)
        return " | ".join(results[:3]) if results else "No results"
    except:
        return "Search error"

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
    if "weather" in msg:
        loc = re.search(r'in\s+(\w+)', msg)
        return get_weather(loc.group(1) if loc else "Tokyo")
    if "stock" in msg or "$" in msg:
        sym = re.findall(r'[A-Z]{2,5}', msg.upper())
        return get_stock(sym[0] if sym else "AAPL")
    if "search" in msg:
        query = message.replace("search", "").replace("for", "").strip()
        return web_search(query) if query else None
    return None

def chat(message, history, provider="ollama"):
    if not message.strip():
        return "", history
    
    msg_lower = message.lower().strip()
    
    # Identity
    identity = ["what is your name", "who are you", "your name", "who created"]
    if any(t in msg_lower for t in identity):
        history.append({"role": "user", "content": message})
        reply = "I am Diskova+ AI, created by Joseph Amaning Kwarteng from Ghana."
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    # Hello
    if "hello" in msg_lower or "hi" in msg_lower:
        history.append({"role": "user", "content": message})
        reply = "Hello! How can I help you?"
        history.append({"role": "assistant", "content": reply})
        return "", history
    
    history.append({"role": "user", "content": message})
    reply = "Thinking..."
    
    # Tool first
    tool = auto_tool(message)
    if tool:
        reply = tool
    else:
        reply = chat_ollama(message) if provider == "ollama" else chat_zen(message, PROVIDERS[provider]["model"])
    
    history.append({"role": "assistant", "content": reply})
    return "", history

# ==================== GUI ====================

internet = check_internet()
ollama = check_ollama()

css = """
.gradio-container { max-width: 1400px !important; margin: auto !important; }
.chatbot { min-height: 500px !important; }
.footer { color: #666; font-size: 12px; text-align: center; margin-top: 20px; }
"""

with gr.Blocks(css=css, title=APP_NAME) as app:
    
    gr.Markdown(f"# {APP_NAME}")
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(height=550)
            with gr.Row():
                msg = gr.Textbox(placeholder="Message... (Enter to send)", scale=5, show_label=False)
                btn = gr.Button("Send", variant="primary")
        
        with gr.Column(scale=1, visible=False):
            gr.Markdown("### Settings")
            provider = gr.Dropdown(list(PROVIDERS.keys()), value="ollama", label="Model")
    
    gr.Markdown(f'<div class="footer">Status: {"Online" if internet else "Offline"} | Ollama: {"Running" if ollama else "Not Running"} | {APP_NAME}</div>')
    
    btn.click(chat, [msg, chatbot], [msg, chatbot])
    msg.submit(chat, [msg, chatbot], [msg, chatbot])

print(f"{APP_NAME} - http://localhost:7860")
app.launch(server_name="0.0.0.0", server_port=7860)