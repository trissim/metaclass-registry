from __future__ import annotations

from pathlib import Path


def get_home_dir() -> str:
    """
    Get the user's home directory in a cross-platform manner.
    
    Uses pathlib.Path.home() which works reliably on Unix and Windows.
    
    Returns:
        str: The user's home directory path.
    """
    return str(Path.home())
