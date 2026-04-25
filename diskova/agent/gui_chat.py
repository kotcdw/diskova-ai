#!/usr/bin/env python
"""
Diskova AI - Chat Interface
========================
A clean Gradio chat interface.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import gradio as gr
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "gradio", "-q"])
    import gradio as gr

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

current_model = "qwen2.5-coder:1.5b"


def chat(message, history):
    if not message:
        return "", history
    
    history.append([message, None])
    
    try:
        import requests
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": current_model,
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
        reply = f"Ollama not available: {str(e)[:100]}"
    
    history[-1][1] = reply
    return "", history


def create_gui():
    with gr.Blocks(title="Diskova AI") as app:
        gr.Markdown("# Diskova AI\n\nYour local AI coding assistant")
        
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
                    examples=[
                        ["Hello"],
                        ["Write hello in Python"],
                    ],
                    inputs=msg_input,
                )
        
        submit_btn.click(chat, [msg_input, chatbot], [msg_input, chatbot])
        msg_input.submit(chat, [msg_input, chatbot], [msg_input, chatbot])
    
    return app


def main():
    app = create_gui()
    app.launch(
        server_port=7860,
        server_name="0.0.0.0",
        show_error=True,
    )

if __name__ == "__main__":
    main()