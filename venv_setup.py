import sys
import os

def setup_venv():
    venv_path = os.path.join(os.path.dirname(__file__), 'projet', 'Lib', 'site-packages')
    if venv_path not in sys.path:
        sys.path.insert(0, venv_path)

# Automatically call setup_venv when the module is imported
setup_venv()