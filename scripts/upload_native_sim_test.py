#!/usr/bin/env python3
"""
Simple upload script for Zephyr native_sim Unity tests
"""

import os
import subprocess
import sys

# Get environment variables
PROJECT_DIR = os.environ.get('PROJECT_DIR', os.getcwd())
BUILD_DIR = os.environ.get('BUILD_DIR', os.path.join(PROJECT_DIR, '.pio', 'build', 'native_sim_test'))

print("🧪 Running native_sim Unity tests")
print(f"📁 Project dir: {PROJECT_DIR}")
print(f"🔨 Build dir: {BUILD_DIR}")

# Look for the test executable
test_runner_path = os.path.join(BUILD_DIR, 'test_runner.exe')

if not os.path.exists(test_runner_path):
    print(f"❌ Error: Test executable not found: {test_runner_path}")
    exit(1)

print(f"🧪 Running test executable: {test_runner_path}")

try:
    # Run the test executable with a reasonable timeout
    result = subprocess.run([test_runner_path], timeout=30, capture_output=False, text=True)
    
    # Exit with the same code as the test executable
    exit(result.returncode)
    
except subprocess.TimeoutExpired:
    print("❌ Test execution timed out after 30 seconds")
    exit(1)
except FileNotFoundError:
    print(f"❌ Error: Could not execute {test_runner_path}")
    exit(1)
except Exception as e:
    print(f"❌ Error running tests: {e}")
    exit(1)

