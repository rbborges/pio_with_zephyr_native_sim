#!/usr/bin/env python3
"""
Simple build script for Zephyr native_sim regular application
"""

import os
import subprocess
import shutil
import sys

# Get environment variables
PROJECT_DIR = os.environ.get('PROJECT_DIR', os.getcwd())
BUILD_DIR = os.environ.get('BUILD_DIR', os.path.join(PROJECT_DIR, '.pio', 'build', 'native_sim'))
ZEPHYR_BASE = os.path.expanduser('~/zephyrproject')

# Check if we're being called from SCons
using_scons = len(sys.argv) > 1 and 'scons' in str(sys.argv)
if using_scons:
    Import("env")

print("🚀 Building Zephyr native_sim application")
print(f"📁 Project dir: {PROJECT_DIR}")
print(f"🔨 Build dir: {BUILD_DIR}")

# Ensure build directory exists
os.makedirs(BUILD_DIR, exist_ok=True)

# Use the original zephyr directory for regular builds
zephyr_dir = os.path.join(PROJECT_DIR, 'zephyr')

if not os.path.exists(zephyr_dir):
    print(f"❌ Error: Zephyr directory not found: {zephyr_dir}")
    if using_scons:
        env.Exit(1)
    else:
        exit(1)

print("🔧 Building regular application...")

# Run west build for regular application
print("⚡ Running: west build -b native_sim --pristine always")

# Prepare build command with virtual environment activation
full_command = (f". {ZEPHYR_BASE}/.venv/bin/activate && "
               f"cd {ZEPHYR_BASE} && "
               f"west build -b native_sim --pristine always {zephyr_dir}")

try:
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=120)
    
    if result.returncode == 0:
        print("✅ Zephyr native_sim build successful!")
    else:
        print("❌ Zephyr build failed!")
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

# Copy the built executable to PlatformIO expected locations
zephyr_exe_path = os.path.join(ZEPHYR_BASE, 'build', 'zephyr', 'zephyr.exe')
firmware_path = os.path.join(BUILD_DIR, 'firmware.bin')

if os.path.exists(zephyr_exe_path):
    print(f"🎯 Application executable: {zephyr_exe_path}")
    
    # Copy with robust error handling
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Remove existing file first if it exists
            if os.path.exists(firmware_path):
                try:
                    os.remove(firmware_path)
                except OSError:
                    # If we can't remove it, try atomic replacement
                    temp_path = firmware_path + '.tmp'
                    shutil.copy(zephyr_exe_path, temp_path)
                    os.replace(temp_path, firmware_path)
                    break
            
            # Copy the file
            shutil.copy(zephyr_exe_path, firmware_path)
            break
            
        except OSError as e:
            if "Text file busy" in str(e) and attempt < max_retries - 1:
                print(f"⚠️  File busy, retrying... (attempt {attempt + 1}/{max_retries})")
                import time
                time.sleep(0.5)  # Wait before retrying
                continue
            else:
                print(f"❌ Error copying executable: {e}")
                if using_scons:
                    env.Exit(1)
                else:
                    exit(1)
    
    # Set execute permissions
    os.chmod(firmware_path, 0o755)
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
        print("✨ Custom Zephyr build completed")
        return None

    # Replace the program builder
    env.Replace(BUILDERS={'BuildProgram': env.Builder(action=custom_program_builder)})

    # Set the program path for regular builds
    program_path = os.path.join(BUILD_DIR, 'firmware.bin')
    env.Replace(PROGPATH=program_path)
    env.Replace(PROGNAME='firmware.bin')
    
    # Ensure the program path exists in the environment
    if os.path.exists(program_path):
        print(f"📍 Program path set: {program_path}")
        # Create a dummy target for PlatformIO
        env.Default(env.Alias("buildprog", program_path))
    else:
        print(f"⚠️  Warning: Program path does not exist yet: {program_path}")
        # Create the target anyway for PlatformIO
        env.Default(env.Alias("buildprog", []))

print("🎉 Application build complete!")

