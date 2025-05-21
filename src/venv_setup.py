import sys
import os

def setup_venv():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    venv_path = os.path.join(base_path, 'projet', 'Lib', 'site-packages')
    if venv_path not in sys.path:
        sys.path.insert(0, venv_path)

# Automatically call setup_venv when the module is imported
setup_venv()