#!/usr/bin/env python
"""Diskova AI - Startup Script"""
import subprocess
import sys
import os

os.chdir(r"C:\Users\GPHA-TM\Desktop\RESEARCH\diskova+")
p = subprocess.Popen([sys.executable, "diskova/agent/gui_chat.py"],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     creationflags=subprocess.CREATE_NO_WINDOW)
print(f"Started GUI, PID: {p.pid}")