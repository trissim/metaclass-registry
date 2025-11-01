"""
metaclass-registry: Zero-boilerplate metaclass-driven plugin registry system.

This package provides a generic metaclass infrastructure for automatic plugin
registration with lazy discovery, caching, and zero boilerplate.
"""

__version__ = "0.1.0"

from .core import (
    AutoRegisterMeta, 
    RegistryConfig, 
    PRIMARY_KEY,
    LazyDiscoveryDict,
    SecondaryRegistry,
    SecondaryRegistryDict,
    extract_key_from_handler_suffix
)
from .discovery import discover_registry_classes
from .cache import RegistryCacheManager
from .exceptions import RegistryError, DiscoveryError, CacheError

__all__ = [
    # Core
    "AutoRegisterMeta",
    "RegistryConfig",
    "PRIMARY_KEY",
    # Discovery
    "LazyDiscoveryDict",
    "discover_registry_classes",
    # Cache
    "RegistryCacheManager",
    # Helpers
    "SecondaryRegistry",
    "SecondaryRegistryDict",
    "extract_key_from_handler_suffix",
    # Exceptions
    "RegistryError",
    "DiscoveryError",
    "CacheError",
]
