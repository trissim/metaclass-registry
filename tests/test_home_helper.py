import os
import sys
import pytest

from metaclass_registry import _home


def test_get_home_windows(monkeypatch, tmp_path):
    """Test Windows strategy uses USERPROFILE."""
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    assert _home.get_home_dir() == str(tmp_path)


def test_get_home_unix(monkeypatch, tmp_path):
    """Test Unix strategy uses HOME."""
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("HOME", str(tmp_path))
    assert _home.get_home_dir() == str(tmp_path)


def test_get_home_windows_missing_env(monkeypatch):
    """Test Windows raises when USERPROFILE is not set."""
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.delenv("USERPROFILE", raising=False)
    with pytest.raises(RuntimeError, match="USERPROFILE environment variable is not set"):
        _home.get_home_dir()


def test_get_home_unix_missing_env(monkeypatch):
    """Test Unix raises when HOME is not set."""
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("HOME", raising=False)
    with pytest.raises(RuntimeError, match="HOME environment variable is not set"):
        _home.get_home_dir()
