"""Tests for metaclass_registry.discovery module."""

import importlib
import sys
import tempfile
from pathlib import Path
from typing import Type

import pytest

from metaclass_registry.discovery import (
    discover_registry_classes,
    discover_registry_classes_recursive,
)


class TestDiscoverRegistryClasses:
    """Test discover_registry_classes function."""

    def test_discover_simple_classes(self, tmp_path):
        """Test discovering classes from a simple package."""
        # Create a temporary package structure
        pkg_dir = tmp_path / "test_pkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Create a base class module
        (pkg_dir / "base.py").write_text(
            """
class BasePlugin:
    pass
"""
        )

        # Create plugin modules
        (pkg_dir / "plugin_a.py").write_text(
            """
from .base import BasePlugin

class PluginA(BasePlugin):
    pass
"""
        )

        (pkg_dir / "plugin_b.py").write_text(
            """
from .base import BasePlugin

class PluginB(BasePlugin):
    pass
"""
        )

        # Add to sys.path
        sys.path.insert(0, str(tmp_path))
        try:
            # Import the base module
            base_module = importlib.import_module("test_pkg.base")
            BasePlugin = base_module.BasePlugin

            # Import package
            pkg = importlib.import_module("test_pkg")

            # Discover classes
            discovered = discover_registry_classes(
                package_path=pkg.__path__,
                package_prefix="test_pkg.",
                base_class=BasePlugin,
                exclude_modules={'base'},
            )

            # Should find PluginA and PluginB
            assert len(discovered) == 2
            names = {cls.__name__ for cls in discovered}
            assert names == {'PluginA', 'PluginB'}

        finally:
            # Clean up sys.path
            sys.path.remove(str(tmp_path))
            # Remove from sys.modules
            for key in list(sys.modules.keys()):
                if key.startswith('test_pkg'):
                    del sys.modules[key]

    def test_exclude_modules(self, tmp_path):
        """Test excluding specific modules from discovery."""
        # Create a temporary package structure
        pkg_dir = tmp_path / "test_pkg2"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Create base class
        (pkg_dir / "base.py").write_text(
            """
class BasePlugin:
    pass
"""
        )

        # Create plugin modules
        (pkg_dir / "plugin.py").write_text(
            """
from .base import BasePlugin

class Plugin(BasePlugin):
    pass
"""
        )

        (pkg_dir / "test_plugin.py").write_text(
            """
from .base import BasePlugin

class TestPlugin(BasePlugin):
    pass
"""
        )

        sys.path.insert(0, str(tmp_path))
        try:
            base_module = importlib.import_module("test_pkg2.base")
            BasePlugin = base_module.BasePlugin
            pkg = importlib.import_module("test_pkg2")

            # Discover classes, excluding test modules
            discovered = discover_registry_classes(
                package_path=pkg.__path__,
                package_prefix="test_pkg2.",
                base_class=BasePlugin,
                exclude_modules={'base', 'test_plugin'},
            )

            # Should only find Plugin, not TestPlugin
            # Note: exclude_modules checks if substring is in module name
            # 'test_plugin' will match 'test_pkg2.test_plugin'
            assert len(discovered) == 1
            assert discovered[0].__name__ == 'Plugin'

        finally:
            sys.path.remove(str(tmp_path))
            for key in list(sys.modules.keys()):
                if key.startswith('test_pkg2'):
                    del sys.modules[key]

    def test_validation_func(self, tmp_path):
        """Test using a validation function to filter classes."""
        pkg_dir = tmp_path / "test_pkg3"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "base.py").write_text(
            """
class BasePlugin:
    enabled = True
"""
        )

        (pkg_dir / "plugin_a.py").write_text(
            """
from .base import BasePlugin

class PluginA(BasePlugin):
    enabled = True
"""
        )

        (pkg_dir / "plugin_b.py").write_text(
            """
from .base import BasePlugin

class PluginB(BasePlugin):
    enabled = False
"""
        )

        sys.path.insert(0, str(tmp_path))
        try:
            base_module = importlib.import_module("test_pkg3.base")
            BasePlugin = base_module.BasePlugin
            pkg = importlib.import_module("test_pkg3")

            # Only accept enabled plugins
            def validate(cls):
                return getattr(cls, 'enabled', False) is True

            discovered = discover_registry_classes(
                package_path=pkg.__path__,
                package_prefix="test_pkg3.",
                base_class=BasePlugin,
                exclude_modules={'base'},
                validation_func=validate,
            )

            # Should only find PluginA
            assert len(discovered) == 1
            assert discovered[0].__name__ == 'PluginA'

        finally:
            sys.path.remove(str(tmp_path))
            for key in list(sys.modules.keys()):
                if key.startswith('test_pkg3'):
                    del sys.modules[key]

    def test_no_classes_found(self, tmp_path):
        """Test when no matching classes are found."""
        pkg_dir = tmp_path / "test_pkg4"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "base.py").write_text(
            """
class BasePlugin:
    pass
"""
        )

        # Module with no plugin classes
        (pkg_dir / "utils.py").write_text(
            """
def helper():
    pass
"""
        )

        sys.path.insert(0, str(tmp_path))
        try:
            base_module = importlib.import_module("test_pkg4.base")
            BasePlugin = base_module.BasePlugin
            pkg = importlib.import_module("test_pkg4")

            discovered = discover_registry_classes(
                package_path=pkg.__path__,
                package_prefix="test_pkg4.",
                base_class=BasePlugin,
                exclude_modules={'base'},
            )

            assert len(discovered) == 0

        finally:
            sys.path.remove(str(tmp_path))
            for key in list(sys.modules.keys()):
                if key.startswith('test_pkg4'):
                    del sys.modules[key]


class TestDiscoverRegistryClassesRecursive:
    """Test discover_registry_classes_recursive function."""

    def test_recursive_discovery(self, tmp_path):
        """Test recursive discovery through nested packages."""
        # Create nested package structure
        pkg_dir = tmp_path / "test_pkg5"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Base class
        (pkg_dir / "base.py").write_text(
            """
class BasePlugin:
    pass
"""
        )

        # Top-level plugin
        (pkg_dir / "plugin_top.py").write_text(
            """
from .base import BasePlugin

class PluginTop(BasePlugin):
    pass
"""
        )

        # Nested subpackage
        sub_dir = pkg_dir / "subpackage"
        sub_dir.mkdir()
        (sub_dir / "__init__.py").write_text("")

        (sub_dir / "plugin_sub.py").write_text(
            """
from ..base import BasePlugin

class PluginSub(BasePlugin):
    pass
"""
        )

        sys.path.insert(0, str(tmp_path))
        try:
            base_module = importlib.import_module("test_pkg5.base")
            BasePlugin = base_module.BasePlugin
            pkg = importlib.import_module("test_pkg5")

            # Discover recursively
            discovered = discover_registry_classes_recursive(
                package_path=pkg.__path__,
                package_prefix="test_pkg5.",
                base_class=BasePlugin,
                exclude_modules={'base'},
            )

            # Should find both top-level and nested plugins
            assert len(discovered) >= 2
            names = {cls.__name__ for cls in discovered}
            assert 'PluginTop' in names
            assert 'PluginSub' in names

        finally:
            sys.path.remove(str(tmp_path))
            for key in list(sys.modules.keys()):
                if key.startswith('test_pkg5'):
                    del sys.modules[key]

    def test_deeply_nested_discovery(self, tmp_path):
        """Test discovery through deeply nested package structure."""
        # Create deeply nested structure
        pkg_dir = tmp_path / "test_pkg6"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "base.py").write_text(
            """
class BasePlugin:
    pass
"""
        )

        # Create nested path: level1/level2/level3
        level1 = pkg_dir / "level1"
        level1.mkdir()
        (level1 / "__init__.py").write_text("")

        level2 = level1 / "level2"
        level2.mkdir()
        (level2 / "__init__.py").write_text("")

        level3 = level2 / "level3"
        level3.mkdir()
        (level3 / "__init__.py").write_text("")

        (level3 / "deep_plugin.py").write_text(
            """
from ....base import BasePlugin

class DeepPlugin(BasePlugin):
    pass
"""
        )

        sys.path.insert(0, str(tmp_path))
        try:
            base_module = importlib.import_module("test_pkg6.base")
            BasePlugin = base_module.BasePlugin
            pkg = importlib.import_module("test_pkg6")

            discovered = discover_registry_classes_recursive(
                package_path=pkg.__path__,
                package_prefix="test_pkg6.",
                base_class=BasePlugin,
                exclude_modules={'base'},
            )

            # Should find the deeply nested plugin
            names = {cls.__name__ for cls in discovered}
            assert 'DeepPlugin' in names

        finally:
            sys.path.remove(str(tmp_path))
            for key in list(sys.modules.keys()):
                if key.startswith('test_pkg6'):
                    del sys.modules[key]


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_import_error_handling(self, tmp_path):
        """Test that import errors are handled gracefully."""
        pkg_dir = tmp_path / "test_pkg7"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "base.py").write_text(
            """
class BasePlugin:
    pass
"""
        )

        # Module with import error
        (pkg_dir / "broken.py").write_text(
            """
import nonexistent_module  # This will fail

from .base import BasePlugin

class BrokenPlugin(BasePlugin):
    pass
"""
        )

        # Valid module
        (pkg_dir / "valid.py").write_text(
            """
from .base import BasePlugin

class ValidPlugin(BasePlugin):
    pass
"""
        )

        sys.path.insert(0, str(tmp_path))
        try:
            base_module = importlib.import_module("test_pkg7.base")
            BasePlugin = base_module.BasePlugin
            pkg = importlib.import_module("test_pkg7")

            # Should handle import error and continue
            discovered = discover_registry_classes(
                package_path=pkg.__path__,
                package_prefix="test_pkg7.",
                base_class=BasePlugin,
                exclude_modules={'base'},
            )

            # Should still find ValidPlugin despite broken module
            names = {cls.__name__ for cls in discovered}
            assert 'ValidPlugin' in names
            assert 'BrokenPlugin' not in names

        finally:
            sys.path.remove(str(tmp_path))
            for key in list(sys.modules.keys()):
                if key.startswith('test_pkg7'):
                    del sys.modules[key]

    def test_empty_package(self, tmp_path):
        """Test discovery in an empty package."""
        pkg_dir = tmp_path / "test_pkg8"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "base.py").write_text(
            """
class BasePlugin:
    pass
"""
        )

        sys.path.insert(0, str(tmp_path))
        try:
            base_module = importlib.import_module("test_pkg8.base")
            BasePlugin = base_module.BasePlugin
            pkg = importlib.import_module("test_pkg8")

            discovered = discover_registry_classes(
                package_path=pkg.__path__,
                package_prefix="test_pkg8.",
                base_class=BasePlugin,
                exclude_modules={'base'},
            )

            assert len(discovered) == 0

        finally:
            sys.path.remove(str(tmp_path))
            for key in list(sys.modules.keys()):
                if key.startswith('test_pkg8'):
                    del sys.modules[key]
