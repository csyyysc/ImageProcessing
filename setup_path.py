"""
Centralized path setup for the Image Processing Application

This module ensures that all Python scripts can import project modules
regardless of where they're executed from.

This module should be automatically imported by any entry point.
"""

import os
import sys
from pathlib import Path

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).parent.absolute()


def setup_python_path():
    """Setup Python path for the project"""

    # Add project root to Python path if not already there
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    # Also add subdirectories to ensure all imports work
    subdirs = ['backend', 'frontend', 'shared', 'scripts']
    for subdir in subdirs:
        subdir_path = str(PROJECT_ROOT / subdir)
        if subdir_path not in sys.path:
            sys.path.insert(0, subdir_path)

    # Set PYTHONPATH environment variable for subprocesses
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    new_paths = [str(PROJECT_ROOT)] + [str(PROJECT_ROOT / subdir)
                                       for subdir in subdirs]

    if current_pythonpath:
        all_paths = os.pathsep.join(new_paths) + \
            os.pathsep + current_pythonpath
    else:
        all_paths = os.pathsep.join(new_paths)

    os.environ['PYTHONPATH'] = all_paths


def verify_imports():
    """Verify that critical modules can be imported"""
    try:
        import shared.config
        import backend
        import frontend
        return True
    except ImportError as e:
        print(f"Warning: Import verification failed: {e}")
        return False


# Auto-setup when imported
setup_python_path()

# Verify setup worked (only in development)
if __name__ != "__main__" and os.environ.get('ENV') != 'production':
    if not verify_imports():
        print("Warning: Some imports may fail. Check your Python path setup.")
