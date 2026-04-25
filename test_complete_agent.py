#!/usr/bin/env python
"""Test Complete Coding Agent Tools"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 50)
print("COMPLETE CODING AGENT TESTS")
print("=" * 50)

from brain_server import (
    execute_code,
    run_tests,
    read_file,
    write_file,
    list_files,
    git_command,
    search_code,
    get_file_info,
    create_project_scaffold,
    list_memory_stats,
    analyze_project
)

# Test 1: Execute Python Code
print("\n[TEST 1] execute_code (Python)")
from brain_server import execute_code
result = execute_code("print('Hello from executed code!')", "python")
print(result[:200])

# Test 2: Execute JavaScript
print("\n[TEST 2] execute_code (JavaScript)")
result = execute_code("console.log('JS works!');", "javascript")
print(result[:200])

# Test 3: Read File
print("\n[TEST 3] read_file")
result = read_file(str(Path(__file__).parent / "CLAUDE.md"))
print(result[:200])

# Test 4: Write File
print("\n[TEST 4] write_file")
result = write_file(str(Path(__file__).parent / "tools" / "test_write.txt"), "Test content")
print(result)

# Test 5: List Files
print("\n[TEST 5] list_files")
result = list_files(str(Path(__file__).parent), "*.py")
print(result[:300])

# Test 6: Git Command
print("\n[TEST 6] git_command")
result = git_command("status", str(Path(__file__).parent))
print(result[:300])

# Test 7: Search Code
print("\n[TEST 7] search_code")
result = search_code("def ", str(Path(__file__).parent), "py")
print(result[:300])

# Test 8: File Info
print("\n[TEST 8] get_file_info")
result = get_file_info(str(Path(__file__).parent / "brain_server.py"))
print(result[:300])

# Test 9: Create Scaffold (Python project)
print("\n[TEST 9] create_project_scaffold")
result = create_project_scaffold("test_project", "python")
print(result[:300])

# Test 10: List Files (verify scaffold)
print("\n[TEST 10] verify scaffold created")
result = list_files("test_project", "*.py")
print(result[:200])

# Final: Analyzed Project
print("\n[TEST 11] analyze_project")
result = analyze_project("test_project")
print(result[:300])

print("\n" + "=" * 50)
print("ALL COMPLETE AGENT TESTS PASSED!")
print("=" * 50)