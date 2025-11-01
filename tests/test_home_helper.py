import os
from pathlib import Path

import pytest

from metaclass_registry import _home


def test_get_home_prefers_path_home(monkeypatch, tmp_path):
    # Make Path.home return tmp_path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert _home.get_home_dir() == str(tmp_path)


def test_env_fallback_when_path_home_fails(monkeypatch, tmp_path):
    # Simulate Path.home raising
    def raise_err():
        raise RuntimeError("no go")

    monkeypatch.setattr(Path, "home", raise_err)
    monkeypatch.delenv("HOME", raising=False)
    monkeypatch.delenv("USERPROFILE", raising=False)

    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    assert _home.get_home_dir() == str(tmp_path)


def test_expanduser_fallback_when_no_envs(monkeypatch, tmp_path):
    # Path.home raises, no env vars, expanduser returns a value
    def raise_err():
        raise RuntimeError("nope")

    monkeypatch.setattr(Path, "home", raise_err)

    monkeypatch.delenv("HOME", raising=False)
    monkeypatch.delenv("USERPROFILE", raising=False)

    monkeypatch.setattr(os.path, "expanduser", lambda v: str(tmp_path))
    assert _home.get_home_dir() == str(tmp_path)


def test_final_fallback_to_cwd_when_everything_fails(monkeypatch, tmp_path):
    # Path.home raises, expanduser raises, no envs -> fallback to cwd
    def raise_err():
        raise RuntimeError("bad")

    monkeypatch.setattr(Path, "home", raise_err)
    monkeypatch.delenv("HOME", raising=False)
    monkeypatch.delenv("USERPROFILE", raising=False)

    def expand_raise(v):
        raise RuntimeError("expand fail")

    monkeypatch.setattr(os.path, "expanduser", expand_raise)

    # Change cwd to a known path
    monkeypatch.chdir(str(tmp_path))
    assert _home.get_home_dir() == str(tmp_path)
