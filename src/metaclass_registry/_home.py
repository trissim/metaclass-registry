from __future__ import annotations

import os
from pathlib import Path


def get_home_dir() -> str:
    """
    Robustly determine the user's home directory.

    Order of attempts:
    1. pathlib.Path.home() (recommended; uses OS APIs on Windows)
    2. Environment variables: USERPROFILE, HOME
    3. os.path.expanduser("~")
    4. os.getcwd() as a last resort to avoid raising in CI

    This function is defensive: it swallows exceptions from underlying calls
    so test suites won't crash when CI doesn't provide a home location.
    """
    # 1) Path.home()
    try:
        p = Path.home()
        # Ensure it's non-empty and points to something sensible
        if p and str(p).strip():
            return str(p)
    except Exception:
        # Ignore and continue to fallbacks
        pass

    # 2) Environment variables commonly set on Windows and Unix
    for var in ("USERPROFILE", "HOME"):
        try:
            val = os.environ.get(var)
        except Exception:
            val = None
        if val:
            return val

    # 3) os.path.expanduser
    try:
        expanded = os.path.expanduser("~")
        if expanded and expanded != "~":
            return expanded
    except Exception:
        pass

    # 4) Last resort: use current working directory (deterministic, safe)
    try:
        return os.getcwd()
    except Exception:
        # As an absolute last baseline, return root path for platform
        return os.path.sep
