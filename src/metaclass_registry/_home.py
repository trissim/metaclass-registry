from __future__ import annotations

import os
import sys
from pathlib import Path


def get_home_dir() -> str:
    """
    Determine the user's home directory using platform-specific strategies.

    On Windows: Uses USERPROFILE environment variable.
    On Unix: Uses HOME environment variable.

    Raises:
        RuntimeError: If the home directory cannot be determined.
    """
    if sys.platform == "win32":
        # Windows strategy: use USERPROFILE
        home = os.environ.get("USERPROFILE")
        if not home:
            raise RuntimeError("USERPROFILE environment variable is not set")
        return home
    else:
        # Unix strategy: use HOME
        home = os.environ.get("HOME")
        if not home:
            raise RuntimeError("HOME environment variable is not set")
        return home
