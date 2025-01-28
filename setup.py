import os
import subprocess
import sys

def install_dependencies():
    """Install dependencies using pip."""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def run_game():
    """Run the main game file."""
    subprocess.check_call([sys.executable, os.path.join('src', 'fenetre.py')])

if __name__ == '__main__':
    # Activate the virtual environment
    activate_script = os.path.join('projet', 'Scripts', 'activate')
    if os.name == 'nt':
        activate_script += '.bat'
    subprocess.call(activate_script, shell=True)

    install_dependencies()
    run_game()