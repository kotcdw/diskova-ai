#!/usr/bin/env python
"""Minimal test - does Gradio work?"""

import gradio as gr

def greet(name):
    return f"Hello, {name}!"

with gr.Interface(fn=greet, inputs="text", outputs="text") as demo:
    pass

demo.launch(server_port=7861, share=False)
print("Test GUI running on http://localhost:7861")