import os
import subprocess
import shutil

# Define paths
PROJECT_DIR = os.getcwd()
ZEPHYR_BASE = os.path.expanduser('~/zephyrproject')

if not ZEPHYR_BASE:
    print("Error: ZEPHYR_BASE environment variable not set.")
    print("Please set ZEPHYR_BASE to your Zephyr installation directory.")
    exit(1)

BUILD_DIR  = os.path.join(PROJECT_DIR, '.pio', 'build', 'native_sim_workaround')
OUTPUT_DIR = os.path.join(PROJECT_DIR, '.pio', 'build', 'native_sim_workaround')

# Ensure build directory exists
os.makedirs(BUILD_DIR, exist_ok=True)

# Command to build Zephyr for native_sim
# Assume the Zephyr application source is in the PROJECT_DIR/zephyr
full_command = (f". {ZEPHYR_BASE}/.venv/bin/activate && "
                f"cd {ZEPHYR_BASE} && "
                f"west build -b native_sim {os.path.join(PROJECT_DIR, 'zephyr')} --build-dir {BUILD_DIR}")

print(f"Running Zephyr build command: {' '.join(full_command)}")

try:
    ret = subprocess.run(full_command, check=True, cwd=PROJECT_DIR, shell=True, capture_output=True, text=True)
    print("Zephyr native_sim build successful.")

    # Copy the executable to the PlatformIO output directory
    zephyr_exe_path = os.path.join(BUILD_DIR, 'zephyr', 'zephyr.exe')
    if os.path.exists(zephyr_exe_path):
        shutil.copy(zephyr_exe_path, OUTPUT_DIR)
        print(f"Copied zephyr.exe to {OUTPUT_DIR}")
    else:
        print(f"Warning: zephyr.exe not found at {zephyr_exe_path}")

except subprocess.CalledProcessError as e:
    print(f"Error during Zephyr native_sim build: {e}")
    exit(1)
except FileNotFoundError:
    print("Error: 'west' command not found. Make sure Zephyr SDK and west are installed and in your PATH.")
    exit(1)