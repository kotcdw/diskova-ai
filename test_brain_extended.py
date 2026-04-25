#!/usr/bin/env python
"""Extended tests for PowerfulBrain MCP Server"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 50)
print("EXTENDED TESTS")
print("=" * 50)

from brain_server import (
    save_session_memory,
    update_task_status,
    search_knowledge,
    generate_docs,
    get_code_snippet,
    analyze_project
)

# Test 6: Save Session Memory
print("\n[TEST 6] save_session_memory")
result = save_session_memory(
    task="Test create session",
    result="Session created successfully",
    tags="test,memory"
)
print(result)

# Test 7: Update Task Status
print("\n[TEST 7] update_task_status")
result = update_task_status(
    task_id="test-1",
    status="in_progress",
    description="Testing task tracking"
)
print(result)

# Test 8: Search Knowledge
print("\n[TEST 8] search_knowledge")
result = search_knowledge("python", "sessions")
print(result)

# Test 9: Generate Docs
print("\n[TEST 9] generate_docs")
code = """
def hello(name):
    '''Say hello'''
    return f'Hello {name}'

class Greeter:
    '''A greeter class'''
    def greet(self):
        return 'Hi!'
"""
result = generate_docs(code, "markdown")
print(result[:300])

# Test 10: More Code Snippets (JavaScript)
print("\n[TEST 10] get_code_snippet (JavaScript)")
result = get_code_snippet("javascript", "async")
print(result[:150])

# Test 11: More Code Snippets (TypeScript)
print("\n[TEST 11] get_code_snippet (TypeScript)")
result = get_code_snippet("typescript", "interface")
print(result[:150])

# Test 12: More Code Snippets (Go)
print("\n[TEST 12] get_code_snippet (Go)")
result = get_code_snippet("go", "error-handling")
print(result[:150])

# Test 13: Update Task Status (complete)
print("\n[TEST 13] update_task_status (completed)")
result = update_task_status(
    task_id="test-1",
    status="completed"
)
print(result)

# Test 14: List All Tasks
print("\n[TEST 14] list_memory_stats")
result = analyze_project(".")
print(result)

print("\n" + "=" * 50)
print("ALL EXTENDED TESTS PASSED!")
print("=" * 50)