#!/usr/bin/env python3

import os
import subprocess
import shutil
import sys
import glob

# Try to import SCons environment if available
try:
    from SCons.Script import Import
    Import("env")
    # Get paths from PlatformIO environment
    PROJECT_DIR = env.subst("$PROJECT_DIR")
    BUILD_DIR = env.subst("$BUILD_DIR")
    using_scons = True
except:
    # Fallback for direct execution
    PROJECT_DIR = os.getcwd()
    BUILD_DIR = os.path.join(PROJECT_DIR, '.pio', 'build', 'native_sim')
    using_scons = False

ZEPHYR_BASE = os.path.expanduser('~/zephyrproject')

# Detect operation type based on environment variables and command line
is_test_build = (
    os.environ.get('PIOTEST') == '1' or 
    'test' in sys.argv or 
    any('test' in arg for arg in sys.argv)
)

is_debug_build = (
    'debug' in BUILD_DIR.lower() or 
    os.environ.get('DEBUG') == '1' or
    '-D DEBUG' in ' '.join(sys.argv)
)

# Detect which specific test folder is being built
current_test_folder = None
if is_test_build:
    # Method 1: Try to detect from PlatformIO environment variables
    if using_scons:
        # Check PIOTEST_RUNNING_NAME from SCons environment
        test_name = env.get('PIOTEST_RUNNING_NAME', '')
        if test_name and test_name.startswith('test_'):
            current_test_folder = test_name
        
        # Also check PROJECT_TEST_DIR if available
        test_dir = env.get('PROJECT_TEST_DIR', '')
        if test_dir and not current_test_folder:
            test_dir_parts = test_dir.split(os.sep)
            for part in test_dir_parts:
                if part.startswith('test_'):
                    current_test_folder = part
                    break
    
    # Method 1.5: Check system environment for PIOTEST_RUNNING_NAME (may be base64 encoded)
    if not current_test_folder:
        test_name = os.environ.get('PIOTEST_RUNNING_NAME', '')
        if test_name:
            try:
                # Try to decode from base64 (PlatformIO encodes some values)
                import base64
                decoded_name = base64.b64decode(test_name).decode('utf-8')
                if decoded_name.startswith('test_'):
                    current_test_folder = decoded_name
            except:
                # If decoding fails, try using the raw value
                if test_name.startswith('test_'):
                    current_test_folder = test_name
    
    # Method 2: Try to detect from BUILD_DIR path
    if not current_test_folder:
        build_path_parts = BUILD_DIR.split(os.sep)
        for part in build_path_parts:
            if part.startswith('test_'):
                current_test_folder = part
                break
    
    # Method 3: Check for test folder in command line arguments
    if not current_test_folder:
        for arg in sys.argv:
            if 'test_' in arg:
                # Extract test folder name
                parts = arg.split('/')
                for part in parts:
                    if part.startswith('test_'):
                        current_test_folder = part
                        break
                if current_test_folder:
                    break
    
    # Method 4: Check environment variables that might contain test info
    if not current_test_folder:
        for env_var in ['PIOTEST_RUNNING_NAME', 'PIOTEST_FILTER', 'PIOTEST_IGNORE']:
            env_value = os.environ.get(env_var, '')
            if env_value and 'test_' in env_value:
                parts = env_value.split()
                for part in parts:
                    if part.startswith('test_'):
                        current_test_folder = part
                        break
                if current_test_folder:
                    break
    
    # Method 5: Check if PlatformIO is filtering tests
    if not current_test_folder:
        # Check for -f or --filter argument in command line
        for i, arg in enumerate(sys.argv):
            if arg in ['-f', '--filter'] and i + 1 < len(sys.argv):
                filter_value = sys.argv[i + 1]
                if filter_value.startswith('test_'):
                    current_test_folder = filter_value
                    break
    
    # Method 6: If we still haven't found it, try to detect from the working directory
    if not current_test_folder:
        # Check if there's a specific test directory being processed
        test_base_dir = os.path.join(PROJECT_DIR, 'test')
        if os.path.exists(test_base_dir):
            test_folders = [d for d in os.listdir(test_base_dir) 
                          if os.path.isdir(os.path.join(test_base_dir, d)) and d.startswith('test_')]
            
            # If there's only one test folder, use it
            if len(test_folders) == 1:
                current_test_folder = test_folders[0]
            elif len(test_folders) > 1:
                # Multiple test folders exist, but we couldn't detect which one
                # For now, we'll fall back to building all tests (backward compatibility)
                current_test_folder = None

# Use different build directories for different build types to avoid conflicts
if is_test_build:
    # For test environments, don't add extra _test suffix if already present
    if not BUILD_DIR.endswith('_test'):
        BUILD_DIR = BUILD_DIR + '_test'
elif is_debug_build:
    BUILD_DIR = BUILD_DIR + '_debug'

# Determine build type
if is_test_build:
    build_type = "TEST"
    if current_test_folder:
        print(f"🧪 Building Zephyr native_sim Unity tests for: {current_test_folder}")
    else:
        print("🧪 Building Zephyr native_sim Unity tests")
else:
    build_type = "APPLICATION"
    print("🚀 Building Zephyr native_sim application")

if is_debug_build:
    print("🐛 Debug build enabled")

print(f"📁 Project dir: {PROJECT_DIR}")
print(f"🔨 Build dir: {BUILD_DIR}")
if current_test_folder:
    print(f"📂 Test folder: {current_test_folder}")

# Verify Zephyr installation
if not os.path.exists(ZEPHYR_BASE):
    print("❌ Error: ZEPHYR_BASE not found at ~/zephyrproject")
    print("Please ensure Zephyr is properly installed.")
    if using_scons:
        env.Exit(1)
    else:
        exit(1)

os.makedirs(BUILD_DIR, exist_ok=True)

if is_test_build:
    # Build test application
    print("🔧 Configuring Unity test build...")
    
    # Create test-specific Zephyr application
    test_zephyr_dir = os.path.join(BUILD_DIR, 'test_zephyr_app')
    os.makedirs(test_zephyr_dir, exist_ok=True)
    
    # Copy base Zephyr configuration
    base_zephyr_dir = os.path.join(PROJECT_DIR, 'zephyr')
    if os.path.exists(os.path.join(base_zephyr_dir, 'prj.conf')):
        shutil.copy(os.path.join(base_zephyr_dir, 'prj.conf'), test_zephyr_dir)
    
    # Find Unity library installation
    unity_paths = [
        os.path.join(PROJECT_DIR, '.pio', 'libdeps', 'native_sim_test', 'Unity'),
        os.path.join(PROJECT_DIR, '.pio', 'libdeps', 'native_sim', 'Unity'),
        os.path.join(PROJECT_DIR, '.pio', 'libdeps', '*', 'Unity'),
    ]
    
    unity_path = None
    for path in unity_paths:
        if '*' in path:
            # Handle wildcard paths
            import glob
            matches = glob.glob(path)
            if matches:
                unity_path = matches[0]
                break
        elif os.path.exists(path):
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
    
    # Create CMakeLists.txt for test application
    debug_flags = ""
    if is_debug_build:
        debug_flags = """
# Debug build configuration
target_compile_options(app PRIVATE -g -O0 -DDEBUG)
target_compile_definitions(app PRIVATE DEBUG=1)
"""
    
    cmake_content = f'''cmake_minimum_required(VERSION 3.13.1)
find_package(Zephyr REQUIRED HINTS $ENV{{ZEPHYR_BASE}})
project(zephyr_test_app)

# Include Unity framework
target_sources(app PRIVATE "{unity_path}/src/unity.c")
target_include_directories(app PRIVATE "{unity_path}/src")

# Include test sources from specific folder
{test_sources_pattern}
target_sources(app PRIVATE ${{test_sources}})

# Include library sources
file(GLOB_RECURSE lib_sources "{PROJECT_DIR}/lib/*.c")
target_sources(app PRIVATE ${{lib_sources}})

# Include directories (exclude src to avoid main application)
target_include_directories(app PRIVATE "{PROJECT_DIR}/test/include_shims")

# Include library directories
file(GLOB_RECURSE lib_include_dirs LIST_DIRECTORIES true "{PROJECT_DIR}/lib/*")
foreach(dir ${{lib_include_dirs}})
    if(IS_DIRECTORY ${{dir}})
        target_include_directories(app PRIVATE ${{dir}})
    endif()
endforeach()

{debug_flags}
'''    
    # Write CMakeLists.txt
    cmake_path = os.path.join(test_zephyr_dir, 'CMakeLists.txt')
    with open(cmake_path, 'w') as f:
        f.write(cmake_content)
    
    print(f"📝 Created CMakeLists.txt: {cmake_path}")
    
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
    except Exception as e:
        print(f"❌ Build error: {e}")
        if using_scons:
            env.Exit(1)
        else:
            exit(1)

else:
    # Build regular application
    print("🔧 Configuring application build...")
    
    # Use the existing zephyr directory for regular builds
    zephyr_dir = os.path.join(PROJECT_DIR, 'zephyr')
    
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
    except Exception as e:
        print(f"❌ Build error: {e}")
        if using_scons:
            env.Exit(1)
        else:
            exit(1)

# Copy the built executable to the expected location
zephyr_build_dir = os.path.join(ZEPHYR_BASE, 'build')
zephyr_exe_path = os.path.join(zephyr_build_dir, 'zephyr', 'zephyr.exe')

if os.path.exists(zephyr_exe_path):
    if is_test_build:
        # For test builds, copy as test_runner.exe
        test_dest = os.path.join(BUILD_DIR, 'test_runner.exe')
        shutil.copy(zephyr_exe_path, test_dest)
        print(f"🧪 Test executable: {test_dest}")
    else:
        # For regular builds, copy as zephyr.exe
        zephyr_dest = os.path.join(BUILD_DIR, 'zephyr.exe')
        shutil.copy(zephyr_exe_path, zephyr_dest)
        print(f"🎯 Application executable: {zephyr_dest}")

    # Always copy as firmware.bin for PlatformIO compatibility
    firmware_path = os.path.join(BUILD_DIR, 'firmware.bin')
    
    # Robust file copying to handle "Text file busy" errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Remove existing file first if it exists
            if os.path.exists(firmware_path):
                try:
                    os.remove(firmware_path)
                except OSError:
                    # If we can't remove it, try a different approach
                    import tempfile
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
                time.sleep(0.5)  # Wait a bit before retrying
                continue
            else:
                # If all retries failed or it's a different error
                print(f"❌ Error copying executable: {e}")
                if using_scons:
                    env.Exit(1)
                else:
                    exit(1)
    
    # Set execute permissions
    if is_test_build:
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

    # Set the program path based on build type
    if is_test_build:
        # For test builds, use test_runner.exe which contains the Unity tests
        program_path = os.path.join(BUILD_DIR, 'test_runner.exe')
        env.Replace(PROGPATH=program_path)
        env.Replace(PROGNAME='test_runner.exe')
        # Set upload command for test execution
        env.Replace(UPLOADCMD=f"python3 {PROJECT_DIR}/scripts/upload_zephyr_native_sim.py")
        # Ensure PlatformIO knows this is a test environment
        env.Append(CPPDEFINES=['UNIT_TEST'])
    else:
        # For regular builds, use firmware.bin
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

print(f"🎉 Build complete! Type: {build_type}")
if current_test_folder:
    print(f"📂 Test folder: {current_test_folder}")

