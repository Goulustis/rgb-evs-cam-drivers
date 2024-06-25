import subprocess
import time
import sys
from config import GREEN, RESET, SCENE, RUN_DURATION

def start_camera_scripts():
    print(f"making {GREEN}{SCENE}{RESET} for {RUN_DURATION} sec")
    # Command for starting rgb.py with the scene argument
    rgb_command = ['python3', 'rgb_script.py']

    # Command for starting evs.py with the scene argument
    evs_command = ['python3', 'record_triggers_and_events.py']
    
    # Start evs.py as a subprocess
    evs_process = subprocess.Popen(evs_command)
    
    time.sleep(0.05)

    # Start rgb.py as a subprocess
    rgb_process = subprocess.Popen(rgb_command)

    # Wait for both processes to complete (optional)
    rgb_stdout, rgb_stderr = rgb_process.communicate()
    evs_stdout, evs_stderr = evs_process.communicate()


if __name__ == '__main__':
    start_camera_scripts()

