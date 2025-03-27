import subprocess
import sys
import os
import platform
import venv

def create_virtualenv():
    """Create a virtual environment if it doesn't exist."""
    if not os.path.exists('projet'):
        print("Creating virtual environment...")
        venv.create('projet', with_pip=True)
    else:
        print("Virtual environment already exists.")

def activate_virtualenv():
    """Activate the virtual environment."""
    if platform.system() == "Windows":
        activate_script = os.path.join("projet", "Scripts", "activate.bat")
        print(f"Activating virtual environment using {activate_script}...")
        subprocess.call(activate_script, shell=True)
    else:
        activate_script = os.path.join("projet", "bin", "activate")
        print(f"Activating virtual environment using {activate_script}...")
        subprocess.call(f"source {activate_script}", shell=True, executable="/bin/bash")

def install_dependencies():
    """Install dependencies using pip."""
    python_executable = os.path.join('projet', 'Scripts', 'python') if platform.system() == "Windows" else os.path.join('projet', 'bin', 'python')
    print("Installing dependencies...")
    subprocess.check_call([python_executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def run_game():
    """Run the main game file."""
    python_executable = os.path.join('projet', 'Scripts', 'python') if platform.system() == "Windows" else os.path.join('projet', 'bin', 'python')
    print("Running the game...")
    subprocess.check_call([python_executable, os.path.join('src', 'fenetre.py')])

if __name__ == "__main__":
    create_virtualenv()
    activate_virtualenv()
    install_dependencies()
    run_game()