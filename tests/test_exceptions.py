"""Tests for metaclass_registry.exceptions module."""

import pytest

from metaclass_registry.exceptions import RegistryError, DiscoveryError, CacheError


class TestExceptions:
    """Test exception classes."""

    def test_registry_error(self):
        """Test RegistryError exception."""
        with pytest.raises(RegistryError, match="test error"):
            raise RegistryError("test error")

        # Test inheritance
        assert issubclass(RegistryError, Exception)

    def test_discovery_error(self):
        """Test DiscoveryError exception."""
        with pytest.raises(DiscoveryError, match="discovery failed"):
            raise DiscoveryError("discovery failed")

        # Test inheritance
        assert issubclass(DiscoveryError, RegistryError)
        assert issubclass(DiscoveryError, Exception)

    def test_cache_error(self):
        """Test CacheError exception."""
        with pytest.raises(CacheError, match="cache failed"):
            raise CacheError("cache failed")

        # Test inheritance
        assert issubclass(CacheError, RegistryError)
        assert issubclass(CacheError, Exception)

    def test_exception_catching(self):
        """Test that specific exceptions can be caught as RegistryError."""
        try:
            raise DiscoveryError("test")
        except RegistryError:
            pass  # Should catch it

        try:
            raise CacheError("test")
        except RegistryError:
            pass  # Should catch it
