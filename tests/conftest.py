"""Pytest configuration and fixtures for metaclass_registry tests."""

import sys
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def reset_registries():
    """
    Reset any module-level registries between tests.

    This prevents test pollution where one test's registry modifications
    affect another test.
    """
    yield
    # Cleanup code after test runs
    # Remove any test modules from sys.modules
    to_remove = [key for key in sys.modules.keys() if 'test_pkg' in key]
    for key in to_remove:
        del sys.modules[key]


@pytest.fixture
def temp_package(tmp_path):
    """
    Create a temporary package structure for testing.

    Returns the package directory path.
    """
    pkg_dir = tmp_path / "temp_pkg"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text("")
    return pkg_dir
