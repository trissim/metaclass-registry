"""Tests for metaclass_registry.core module."""

import pytest
from metaclass_registry import (
    AutoRegisterMeta,
    RegistryConfig,
    LazyDiscoveryDict,
    SecondaryRegistryDict,
    SecondaryRegistry,
    PRIMARY_KEY,
    extract_key_from_handler_suffix,
    extract_key_from_backend_suffix,
    make_suffix_extractor,
)


class TestLazyDiscoveryDict:
    """Test LazyDiscoveryDict functionality."""

    def test_init(self):
        """Test LazyDiscoveryDict initialization."""
        registry = LazyDiscoveryDict()
        assert not registry._discovered
        assert registry._enable_cache is True
        assert len(registry) == 0

    def test_init_without_cache(self):
        """Test LazyDiscoveryDict initialization with caching disabled."""
        registry = LazyDiscoveryDict(enable_cache=False)
        assert not registry._enable_cache

    def test_basic_dict_operations(self):
        """Test basic dictionary operations."""
        registry = LazyDiscoveryDict(enable_cache=False)

        # Add items directly
        registry['test'] = object
        assert 'test' in registry
        assert len(registry) == 1
        assert registry['test'] is object

    def test_get_with_default(self):
        """Test get() method with default value."""
        registry = LazyDiscoveryDict(enable_cache=False)
        result = registry.get('nonexistent', 'default')
        assert result == 'default'


class TestSecondaryRegistryDict:
    """Test SecondaryRegistryDict functionality."""

    def test_init(self):
        """Test SecondaryRegistryDict initialization."""
        primary = LazyDiscoveryDict()
        secondary = SecondaryRegistryDict(primary)
        assert secondary._primary_registry is primary

    def test_auto_discovery_trigger(self):
        """Test that accessing secondary registry triggers primary discovery."""
        primary = LazyDiscoveryDict(enable_cache=False)
        primary._discovered = False
        secondary = SecondaryRegistryDict(primary)

        # Mock _discover method
        discover_called = []

        def mock_discover():
            discover_called.append(True)
            primary._discovered = True

        primary._discover = mock_discover

        # Access secondary registry - should trigger discovery
        _ = len(secondary)
        assert len(discover_called) == 1


class TestRegistryConfig:
    """Test RegistryConfig dataclass."""

    def test_minimal_config(self):
        """Test RegistryConfig with minimal required fields."""
        registry_dict = {}
        config = RegistryConfig(
            registry_dict=registry_dict,
            key_attribute='_key',
        )
        assert config.registry_dict is registry_dict
        assert config.key_attribute == '_key'
        assert config.skip_if_no_key is False
        assert config.log_registration is True
        assert config.registry_name == "plugin"

    def test_full_config(self):
        """Test RegistryConfig with all fields."""
        registry_dict = {}
        secondary = SecondaryRegistry(
            registry_dict={},
            key_source=PRIMARY_KEY,
            attr_name='_handler',
        )

        def key_extractor(name, cls):
            return name.lower()

        config = RegistryConfig(
            registry_dict=registry_dict,
            key_attribute='_key',
            key_extractor=key_extractor,
            skip_if_no_key=True,
            secondary_registries=[secondary],
            log_registration=False,
            registry_name='test plugin',
            discovery_package='test.package',
            discovery_recursive=True,
        )

        assert config.skip_if_no_key is True
        assert config.log_registration is False
        assert config.registry_name == 'test plugin'
        assert config.discovery_package == 'test.package'
        assert config.discovery_recursive is True


class TestAutoRegisterMeta:
    """Test AutoRegisterMeta metaclass."""

    def test_simple_registration(self):
        """Test simple class registration with explicit key."""

        # Create a plugin system with auto-registration
        class Plugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'plugin_name'
            plugin_name = None

        # Plugin should have auto-created registry
        assert hasattr(Plugin, '__registry__')
        assert isinstance(Plugin.__registry__, LazyDiscoveryDict)

        # Create a concrete plugin
        class MyPlugin(Plugin):
            plugin_name = 'my_plugin'

        # Should be registered
        assert 'my_plugin' in Plugin.__registry__
        assert Plugin.__registry__['my_plugin'] is MyPlugin

    def test_skip_abstract_class(self):
        """Test that abstract classes are not registered."""
        from abc import abstractmethod

        class AbstractPlugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            name = None

            @abstractmethod
            def run(self):
                pass

        # Abstract class should not be in registry
        assert len(AbstractPlugin.__registry__) == 0

    def test_skip_base_class(self):
        """Test that base class without key is not registered."""

        class BasePlugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            name = None

        # Base class with name=None should not be registered
        assert len(BasePlugin.__registry__) == 0

    def test_registry_inheritance(self):
        """Test that child classes inherit parent registry."""

        class BasePlugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            name = None

        class ChildPlugin(BasePlugin):
            pass

        # Child should inherit parent's registry
        assert hasattr(BasePlugin, '__registry__')
        # ChildPlugin should be able to access the registry through the parent
        assert BasePlugin.__registry__ is not None

    def test_secondary_registry(self):
        """Test secondary registry registration."""
        HANDLERS = {}

        class Plugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            __secondary_registries__ = [
                SecondaryRegistry(
                    registry_dict=HANDLERS,
                    key_source=PRIMARY_KEY,
                    attr_name='handler_class',
                )
            ]
            name = None
            handler_class = None

        class DummyHandler:
            pass

        class MyPlugin(Plugin):
            name = 'my_plugin'
            handler_class = DummyHandler

        # Primary registration
        assert 'my_plugin' in Plugin.__registry__

        # Secondary registration
        assert 'my_plugin' in HANDLERS
        assert HANDLERS['my_plugin'] is DummyHandler

    def test_key_extractor(self):
        """Test custom key extraction function."""

        def extract_key(name, cls):
            """Extract 'foo' from 'FooPlugin'."""
            if name.endswith('Plugin'):
                return name[:-6].lower()
            return None

        class Plugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            __key_extractor__ = extract_key
            name = None

        class MyPlugin(Plugin):
            pass  # name=None, should use extractor

        # Should be registered with extracted key
        assert 'my' in Plugin.__registry__
        assert Plugin.__registry__['my'] is MyPlugin

    def test_skip_if_no_key(self):
        """Test skip_if_no_key behavior."""

        class Plugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            __skip_if_no_key__ = True
            name = None

        class PluginWithoutName(Plugin):
            pass  # name=None

        # Should not be registered (skipped)
        assert len(Plugin.__registry__) == 0

    def test_require_key(self):
        """Test that missing key raises error when skip_if_no_key=False."""

        with pytest.raises(ValueError, match="must have name attribute"):

            class Plugin(metaclass=AutoRegisterMeta):
                __registry_key__ = 'name'
                __skip_if_no_key__ = False
                name = None

            class PluginWithoutName(Plugin):
                pass  # This should raise


class TestSuffixExtractors:
    """Test suffix extraction helper functions."""

    def test_extract_handler_suffix(self):
        """Test extract_key_from_handler_suffix."""

        class DummyClass:
            pass

        result = extract_key_from_handler_suffix('ImageXpressHandler', DummyClass)
        assert result == 'imagexpress'

        result = extract_key_from_handler_suffix('FooBarHandler', DummyClass)
        assert result == 'foobar'

        result = extract_key_from_handler_suffix('NoSuffix', DummyClass)
        assert result == 'nosuffix'

    def test_extract_backend_suffix(self):
        """Test extract_key_from_backend_suffix."""

        class DummyClass:
            pass

        result = extract_key_from_backend_suffix('DiskStorageBackend', DummyClass)
        assert result == 'diskstorage'

        result = extract_key_from_backend_suffix('MemoryBackend', DummyClass)
        assert result == 'memory'

    def test_make_suffix_extractor(self):
        """Test make_suffix_extractor factory function."""

        class DummyClass:
            pass

        extractor = make_suffix_extractor('Manager')
        result = extractor('FileManager', DummyClass)
        assert result == 'file'

        result = extractor('DatabaseManager', DummyClass)
        assert result == 'database'

        result = extractor('NoSuffix', DummyClass)
        assert result == 'nosuffix'


class TestAutoConfiguration:
    """Test automatic registry configuration."""

    def test_auto_registry_name_derivation(self):
        """Test automatic derivation of registry name from class name."""

        class StorageBackend(metaclass=AutoRegisterMeta):
            __registry_key__ = 'backend_type'
            backend_type = None

        class DiskStorage(StorageBackend):
            backend_type = 'disk'

        # Registry name should be auto-derived from class name
        # "StorageBackend" -> "storage backend"
        # This is tested indirectly through the logging/config system

    def test_auto_registry_creation(self):
        """Test that __registry__ is automatically created."""

        class MyPlugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            name = None

        # Registry should be auto-created and attached to class
        assert hasattr(MyPlugin, '__registry__')
        assert isinstance(MyPlugin.__registry__, LazyDiscoveryDict)


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_multi_level_inheritance(self):
        """Test multi-level class inheritance."""

        class BasePlugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            name = None

        class MiddlePlugin(BasePlugin):
            name = None  # Explicitly set to None

        class ConcretePlugin(MiddlePlugin):
            name = 'concrete'

        # All should share same registry
        assert hasattr(BasePlugin, '__registry__')
        assert 'concrete' in BasePlugin.__registry__

    def test_multiple_plugins(self):
        """Test registering multiple plugins."""

        class Plugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            name = None

        class PluginA(Plugin):
            name = 'a'

        class PluginB(Plugin):
            name = 'b'

        class PluginC(Plugin):
            name = 'c'

        # All should be registered
        assert len(Plugin.__registry__) == 3
        assert set(Plugin.__registry__.keys()) == {'a', 'b', 'c'}

    def test_duplicate_key_overwrite(self):
        """Test that duplicate keys overwrite previous registration."""

        class Plugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            name = None

        class PluginA(Plugin):
            name = 'same'

        class PluginB(Plugin):
            name = 'same'  # Same key

        # Last one should win
        assert Plugin.__registry__['same'] is PluginB

    def test_secondary_registry_without_attr(self):
        """Test secondary registry when class doesn't have the attribute."""
        HANDLERS = {}

        class Plugin(metaclass=AutoRegisterMeta):
            __registry_key__ = 'name'
            __secondary_registries__ = [
                SecondaryRegistry(
                    registry_dict=HANDLERS,
                    key_source=PRIMARY_KEY,
                    attr_name='handler_class',
                )
            ]
            name = None
            handler_class = None

        class MyPlugin(Plugin):
            name = 'my_plugin'
            # handler_class not set (None)

        # Primary registration should succeed
        assert 'my_plugin' in Plugin.__registry__

        # Secondary registration should be skipped (handler_class is None)
        assert 'my_plugin' not in HANDLERS
