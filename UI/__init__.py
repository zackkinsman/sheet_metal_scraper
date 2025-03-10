import sys
import os

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    
    Args:
        relative_path: Path relative to the application's base directory
        
    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running as a bundled exe, use the project root directory
        base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    return os.path.join(base_path, relative_path)