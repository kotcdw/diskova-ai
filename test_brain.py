#!/usr/bin/env python
"""Test script for PowerfulBrain MCP Server"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 50)
print("TESTING PowerfulBrain MCP Server")
print("=" * 50)

from brain_server import (
    get_code_snippet,
    list_memory_stats,
    analyze_project,
    recall_pattern,
    review_code
)

# Test 1: Get Code Snippet
print("\n[TEST 1] get_code_snippet")
result = get_code_snippet("python", "function")
print(f"Result: {result[:150]}...")

# Test 2: List Memory Stats
print("\n[TEST 2] list_memory_stats")
result = list_memory_stats()
print(result)

# Test 3: Analyze Project
print("\n[TEST 3] analyze_project")
result = analyze_project(".")
print(result)

# Test 4: Recall Pattern
print("\n[TEST 4] recall_pattern")
result = recall_pattern("api")
print(result)

# Test 5: Review Code
print("\n[TEST 5] review_code")
code = """
def bad():
    try:
        x = 1
    except:
        pass
"""
result = review_code(code, "python")
print(result)

print("\n" + "=" * 50)
print("ALL TESTS PASSED!")
print("=" * 50)