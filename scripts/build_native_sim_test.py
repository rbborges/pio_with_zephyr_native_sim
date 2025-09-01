#!/usr/bin/env python3
"""
Simple build script for Zephyr native_sim Unity tests
"""

import os
import subprocess
import shutil
import sys
import base64

# Get environment variables
PROJECT_DIR = os.environ.get('PROJECT_DIR', os.getcwd())
BUILD_DIR = os.environ.get('BUILD_DIR', os.path.join(PROJECT_DIR, '.pio', 'build', 'native_sim_test'))
ZEPHYR_BASE = os.path.expanduser('~/zephyrproject')

# Check if we're being called from SCons
using_scons = len(sys.argv) > 1 and 'scons' in str(sys.argv)
if using_scons:
    Import("env")

print("🧪 Building Zephyr native_sim Unity tests")
print(f"📁 Project dir: {PROJECT_DIR}")
print(f"🔨 Build dir: {BUILD_DIR}")

# Detect which test folder we're building
current_test_folder = None

# Try multiple methods to detect the test folder
# Method 1: Environment variable
if 'PIOTEST_RUNNING_NAME' in os.environ:
    try:
        encoded_name = os.environ['PIOTEST_RUNNING_NAME']
        current_test_folder = base64.b64decode(encoded_name).decode('utf-8')
        print(f"📂 Test folder (env): {current_test_folder}")
    except:
        print("⚠️  Could not decode test folder name from environment")

# Method 2: Check command line arguments for test filter
if not current_test_folder:
    for arg in sys.argv:
        if arg.startswith('test_'):
            current_test_folder = arg
            print(f"📂 Test folder (args): {current_test_folder}")
            break

# Method 3: For now, just use test_sum as default since the multi-folder detection is complex
# In practice, each test should be run separately anyway
if not current_test_folder:
    current_test_folder = 'test_sum'
    print(f"📂 Test folder (default): {current_test_folder}")

print(f"📂 Building tests for: {current_test_folder}")

# Ensure build directory exists
os.makedirs(BUILD_DIR, exist_ok=True)

# Create a separate test build directory
test_zephyr_dir = os.path.join(BUILD_DIR, 'test_zephyr_app')
os.makedirs(test_zephyr_dir, exist_ok=True)

print("🔧 Configuring Unity test build...")

# Find Unity library
unity_path = None
unity_paths = [
    os.path.join(PROJECT_DIR, '.pio', 'libdeps', 'native_sim_test', 'Unity'),
    os.path.join(PROJECT_DIR, '.pio', 'libdeps', 'native_sim', 'Unity'),
]

for path in unity_paths:
    if os.path.exists(os.path.join(path, 'src', 'unity.c')):
        unity_path = path
        break

if not unity_path:
    print("❌ Error: Unity library not found. Please ensure Unity is installed.")
    print(f"Searched paths: {unity_paths}")
    if using_scons:
        env.Exit(1)
    else:
        exit(1)

print(f"📚 Using Unity from: {unity_path}")

# Determine which test files to include
test_sources_pattern = ""
if current_test_folder:
    # Include only files from the specific test folder
    test_folder_path = os.path.join(PROJECT_DIR, 'test', current_test_folder)
    if os.path.exists(test_folder_path):
        test_sources_pattern = f'file(GLOB test_sources "{test_folder_path}/*.c")'
        print(f"📋 Including tests from: {test_folder_path}")
    else:
        print(f"⚠️  Warning: Test folder not found: {test_folder_path}")
        # Fallback to all test files
        test_sources_pattern = f'file(GLOB_RECURSE test_sources "{PROJECT_DIR}/test/test_*.c")'
else:
    # Fallback: include all test files (for backward compatibility)
    test_sources_pattern = f'file(GLOB_RECURSE test_sources "{PROJECT_DIR}/test/test_*.c")'
    print("📋 Including all test files (no specific folder detected)")

# Create CMakeLists.txt for test application - EXCLUDE ALL MAIN APPLICATION SOURCES
cmake_content = f'''cmake_minimum_required(VERSION 3.13.1)
find_package(Zephyr REQUIRED HINTS $ENV{{ZEPHYR_BASE}})
project(zephyr_test_app)

# Include Unity framework
target_sources(app PRIVATE "{unity_path}/src/unity.c")
target_include_directories(app PRIVATE "{unity_path}/src")

# Include test sources from specific folder
{test_sources_pattern}
target_sources(app PRIVATE ${{test_sources}})

# Include ONLY library sources (NO main application sources)
file(GLOB_RECURSE lib_sources "{PROJECT_DIR}/lib/*.c")
target_sources(app PRIVATE ${{lib_sources}})

# Include directories (EXCLUDE src to avoid main application)
target_include_directories(app PRIVATE "{PROJECT_DIR}/test/include_shims")

# Include library directories
file(GLOB_RECURSE lib_include_dirs LIST_DIRECTORIES true "{PROJECT_DIR}/lib/*")
foreach(dir ${{lib_include_dirs}})
    if(IS_DIRECTORY ${{dir}})
        target_include_directories(app PRIVATE ${{dir}})
    endif()
endforeach()
'''    

# Write CMakeLists.txt
cmake_path = os.path.join(test_zephyr_dir, 'CMakeLists.txt')
with open(cmake_path, 'w') as f:
    f.write(cmake_content)

print(f"📝 Created CMakeLists.txt: {cmake_path}")

# Create prj.conf for test application
prj_conf_content = """# Zephyr Test Configuration
CONFIG_MAIN_STACK_SIZE=4096
CONFIG_HEAP_MEM_POOL_SIZE=4096
CONFIG_PRINTK=y
CONFIG_CONSOLE=y
CONFIG_SERIAL=y
CONFIG_UART_CONSOLE=y
"""

prj_conf_path = os.path.join(test_zephyr_dir, 'prj.conf')
with open(prj_conf_path, 'w') as f:
    f.write(prj_conf_content)

print(f"📝 Created prj.conf: {prj_conf_path}")

# Run west build for test application
print("⚡ Running: west build -b native_sim --pristine always")

# Prepare build command with virtual environment activation
full_command = (f". {ZEPHYR_BASE}/.venv/bin/activate && "
               f"cd {ZEPHYR_BASE} && "
               f"west build -b native_sim --pristine always {test_zephyr_dir}")

try:
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=120)
    
    if result.returncode == 0:
        print("✅ Zephyr native_sim test build successful!")
    else:
        print("❌ Zephyr test build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        if using_scons:
            env.Exit(1)
        else:
            exit(1)
except subprocess.TimeoutExpired:
    print("❌ Build timed out after 120 seconds")
    if using_scons:
        env.Exit(1)
    else:
        exit(1)

# Copy the built test executable to PlatformIO expected locations
zephyr_exe_path = os.path.join(ZEPHYR_BASE, 'build', 'zephyr', 'zephyr.exe')
test_runner_path = os.path.join(BUILD_DIR, 'test_runner.exe')
firmware_path = os.path.join(BUILD_DIR, 'firmware.bin')

if os.path.exists(zephyr_exe_path):
    print(f"🧪 Test executable: {zephyr_exe_path}")
    
    # Copy to test_runner.exe (the correct test executable)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if os.path.exists(test_runner_path):
                os.remove(test_runner_path)
            shutil.copy(zephyr_exe_path, test_runner_path)
            os.chmod(test_runner_path, 0o755)
            break
        except OSError as e:
            if "Text file busy" in str(e) and attempt < max_retries - 1:
                print(f"⚠️  File busy, retrying... (attempt {attempt + 1}/{max_retries})")
                import time
                time.sleep(0.5)
                continue
            else:
                print(f"❌ Error copying test executable: {e}")
                if using_scons:
                    env.Exit(1)
                else:
                    exit(1)
    
    # Also copy to firmware.bin for PlatformIO compatibility
    for attempt in range(max_retries):
        try:
            if os.path.exists(firmware_path):
                os.remove(firmware_path)
            shutil.copy(zephyr_exe_path, firmware_path)
            os.chmod(firmware_path, 0o755)
            break
        except OSError as e:
            if "Text file busy" in str(e) and attempt < max_retries - 1:
                import time
                time.sleep(0.5)
                continue
            else:
                print(f"❌ Error copying firmware.bin: {e}")
                if using_scons:
                    env.Exit(1)
                else:
                    exit(1)
    
    print(f"🧪 Test executable: {test_runner_path}")
    print(f"📦 PlatformIO executable: {firmware_path}")
    
else:
    print(f"❌ Warning: zephyr.exe not found at {zephyr_exe_path}")
    if using_scons:
        env.Exit(1)
    else:
        exit(1)

# Configure SCons environment if available
if using_scons:
    # Override the default build process
    def custom_program_builder(target, source, env):
        print("✨ Custom Zephyr test build completed")
        return None

    # Replace the program builder
    env.Replace(BUILDERS={'BuildProgram': env.Builder(action=custom_program_builder)})

    # Set the program path for test builds - use test_runner.exe
    program_path = os.path.join(BUILD_DIR, 'test_runner.exe')
    env.Replace(PROGPATH=program_path)
    env.Replace(PROGNAME='test_runner.exe')
    
    # Set upload command for test execution
    env.Replace(UPLOADCMD=f"python3 {PROJECT_DIR}/scripts/upload_native_sim_test.py")
    
    # Ensure PlatformIO knows this is a test environment
    env.Append(CPPDEFINES=['UNIT_TEST'])
    
    # Ensure the program path exists in the environment
    if os.path.exists(program_path):
        print(f"📍 Program path set: {program_path}")
        # Create a dummy target for PlatformIO
        env.Default(env.Alias("buildprog", program_path))
    else:
        print(f"⚠️  Warning: Program path does not exist yet: {program_path}")
        # Create the target anyway for PlatformIO
        env.Default(env.Alias("buildprog", []))

print("🎉 Test build complete!")
if current_test_folder:
    print(f"📂 Test folder: {current_test_folder}")

