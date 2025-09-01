#!/usr/bin/env python3

import os
import subprocess
import sys
import time

def main():
    """
    PlatformIO-compatible upload script for Zephyr native_sim
    Handles both regular application runs and test executions
    """
    
    # Get project and build directories from PlatformIO
    project_dir = os.environ.get('PROJECT_DIR', os.getcwd())
    build_dir = os.environ.get('BUILD_DIR', '')
    
    if not build_dir:
        print("❌ Error: BUILD_DIR environment variable not set")
        return 1
    
    # Detect if this is a test run
    is_test_run = (
        os.environ.get('PIOTEST') == '1' or
        os.environ.get('PIOUNITTEST') == '1' or
        'test' in build_dir.lower()
    )
    
    # The build script already handles directory naming, so use BUILD_DIR as-is
    # No need to modify it here
    
    # Look for the executable (try different names based on run type)
    if is_test_run:
        # For test runs, prioritize test_runner.exe which contains the actual Unity tests
        possible_executables = [
            os.path.join(build_dir, 'test_runner.exe'),  # Zephyr test executable (CORRECT for tests)
            os.path.join(build_dir, 'firmware.bin'),     # PlatformIO standard (may contain main app)
            os.path.join(build_dir, 'zephyr.exe'),       # Zephyr native executable (may contain main app)
            os.path.join(build_dir, 'program'),          # Native platform executable
        ]
    else:
        # For regular runs, use the standard application executables
        possible_executables = [
            os.path.join(build_dir, 'firmware.bin'),     # PlatformIO standard (preferred)
            os.path.join(build_dir, 'zephyr.exe'),       # Zephyr native executable
            os.path.join(build_dir, 'program'),          # Native platform executable
        ]
    
    executable = None
    for exe_path in possible_executables:
        if os.path.exists(exe_path) and os.path.isfile(exe_path):
            executable = exe_path
            break
    
    if not executable:
        print(f"❌ Error: No executable found in {build_dir}")
        print(f"Checked paths: {possible_executables}")
        return 1
    
    # Make sure executable has execute permissions
    try:
        os.chmod(executable, 0o755)
    except Exception as e:
        print(f"Warning: Could not set execute permissions: {e}")
    
    if is_test_run:
        print(f"🧪 Running native_sim tests: {os.path.basename(executable)}")
    else:
        print(f"🚀 Running native_sim application: {os.path.basename(executable)}")
    
    try:
        # Use a unified approach for both test and regular runs
        # Set a reasonable timeout for both test and regular runs
        timeout = 60 if is_test_run else 30
        
        # Run the executable with proper output handling
        result = subprocess.run(
            [executable],
            cwd=os.path.dirname(executable),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Forward all output to PlatformIO
        if result.stdout:
            print(result.stdout, end='', flush=True)
        if result.stderr:
            print(result.stderr, end='', flush=True)
        
        # For test runs, look for Unity test results
        if is_test_run and result.returncode == 0:
            output_lines = result.stdout.split('\n') if result.stdout else []
            for line in output_lines:
                if "Tests" in line and "Failures" in line and "Ignored" in line:
                    print(f"📊 Test summary: {line}")
                    break
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print(f"⏰ Execution timed out after {timeout} seconds")
        return 1
    except FileNotFoundError:
        print(f"❌ Executable not found or not executable: {executable}")
        return 1
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

