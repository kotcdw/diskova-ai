#!/usr/bin/env python
"""
Diskova+ AI - Voice GUI (STT + TTS)
=================================
Created by: Joseph Amaning Kwarteng | Ghana
Version: 1.0 | License: MIT
"""

import gradio as gr
import requests
import os
import re
import asyncio

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

CREATOR = "Joseph Amaning Kwarteng"
CREATOR_LOCATION = "Ghana"
APP_NAME = "Diskova+ AI"

try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

try:
    import edge_tts
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


def check_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False


def web_search(query):
    try:
        r = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=10)
        text = r.text
        results = re.findall(r'class="result__snippet">(.*?)</', text)
        if results:
            return " | ".join(results[:3])
        return "No results"
    except Exception as e:
        return f"Search error: {e}"


def get_weather(loc):
    try:
        r = requests.get(f"https://wttr.in/{loc}?format=j1", timeout=10)
        if r.status_code == 200:
            d = r.json()
            c = d.get("current_condition", [{}])[0]
            temp = c.get("temp_C", "N/A")
            desc = c.get("weatherDesc", "N/A")
            if isinstance(desc, list):
                desc = desc[0].get("value", "N/A")
            return f"{loc}: {temp}C, {desc}"
    except Exception as e:
        return f"Weather error: {e}"


def get_stock(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d", timeout=10)
        if r.status_code == 200:
            d = r.json()
            p = d["chart"]["result"][0]["meta"]["regularMarketPrice"]
            return f"{sym}: ${p}"
    except:
        return f"{sym}: unavailable"


def voice_to_text():
    if not VOICE_AVAILABLE:
        return "Voice not available"
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5)
        text = recognizer.recognize_google(audio)
        return text
    except Exception as e:
        return f"Voice error: {str(e)[:30]}"


async def text_to_speech(text):
    if not TTS_AVAILABLE:
        return None
    try:
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
        await communicate.save("response.mp3")
        return "response.mp3"
    except Exception as e:
        return None


def auto_detect_and_tool(message):
    msg = message.lower()
    
    if "weather" in msg:
        loc = re.search(r'in\s+(\w+)', msg)
        location = loc.group(1) if loc else "Tokyo"
        return get_weather(location)
    
    if "stock" in msg or "price" in msg or "$" in msg:
        symbols = re.findall(r'\b[A-Z]{2,5}\b', msg.upper())
        sym = symbols[0] if symbols else "AAPL"
        return get_stock(sym)
    
    if "search" in msg or "find" in msg:
        query = message
        for w in ["search", "find", "look up"]:
            query = query.replace(w, "")
        return web_search(query.strip())
    
    return None


def chat(message, history):
    if not message.strip():
        return "", history
    
    history.append({"role": "user", "content": message})
    reply = "Thinking..."
    
    tool_result = auto_detect_and_tool(message)
    if tool_result:
        reply = tool_result
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
            reply = f"Ollama error: {str(e)[:60]}"
    
    history.append({"role": "assistant", "content": reply})
    return "", history


internet_ok = check_internet()
status = "Online" if internet_ok else "Offline"
voice_status = "Ready" if VOICE_AVAILABLE else "Not Installed"
tts_status = "Ready" if TTS_AVAILABLE else "Not Installed"

with gr.Blocks(title=f"{APP_NAME}") as app:
    gr.Markdown(f"## {APP_NAME}\n**Creator: {CREATOR} | {CREATOR_LOCATION}**\n\n- Status: {status} | Model: {OLLAMA_MODEL}\n\n- Microphone: {voice_status}\n- Speech: {tts_status}**")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=500)
            with gr.Row():
                msg = gr.Textbox(placeholder="Type or click mic...", label="Message", scale=5)
                btn_send = gr.Button("Send", variant="primary")
        
        with gr.Column(scale=1):
            gr.Markdown("### Quick Actions")
            gr.Button("Weather", size="sm").click(lambda: "Tokyo weather", outputs=[msg])
            gr.Button("Stocks", size="sm").click(lambda: "AAPL stock", outputs=[msg])
            gr.Button("Search", size="sm").click(lambda: "Search for AI", outputs=[msg])
            
            gr.Markdown("### Voice Input")
            if VOICE_AVAILABLE:
                gr.Button("Record Mic", variant="stop").click(voice_to_text, outputs=msg)
            
            gr.Markdown("### Voice Output")
            if TTS_AVAILABLE:
                gr.Button("Speak Response", variant="secondary").click(
                    lambda: asyncio.run(text_to_speech("Hello! This is a test response.")),
                    outputs=gr.Audio()
                )
            
            gr.Markdown("### Examples")
            gr.Examples(
                examples=[["Hello!"], ["Weather in Tokyo"], ["AAPL stock"]],
                inputs=msg,
            )
    
    btn_send.click(chat, [msg, chatbot], [msg, chatbot])
    msg.submit(chat, [msg, chatbot], [msg, chatbot])

print("Diskova AI: http://localhost:7860")
app.launch(server_name="0.0.0.0", server_port=7860)