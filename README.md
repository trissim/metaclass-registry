# metaclass-registry

**Zero-boilerplate metaclass-driven plugin registry system with lazy discovery and caching**

[![PyPI version](https://badge.fury.io/py/metaclass-registry.svg)](https://badge.fury.io/py/metaclass-registry)
[![Documentation Status](https://readthedocs.org/projects/metaclass-registry/badge/?version=latest)](https://metaclass-registry.readthedocs.io/en/latest/?badge=latest)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://raw.githubusercontent.com/trissim/metaclass-registry/main/.github/badges/coverage.svg)](https://trissim.github.io/metaclass-registry/coverage/)

## Features

- **Zero Boilerplate**: No custom metaclasses, no manual registry creation, just class attributes
- **Lazy Discovery**: Plugins discovered automatically on first access
- **Registry Inheritance**: Child classes inherit parent's registry for clean interface hierarchies
- **Secondary Registries**: Auto-populate related registries from primary registry
- **Persistent Caching**: Cache discovery results across process restarts
- **Auto-Configuration**: Automatic inference of discovery packages and recursive settings
- **Type-Safe**: Full type hints and mypy support

## Quick Start

```python
from metaclass_registry import AutoRegisterMeta

# Define a base class with registry configuration
class PluginBase(metaclass=AutoRegisterMeta):
    __registry_key__ = 'plugin_name'  # Attribute to use as registry key
    
    plugin_name: str = None  # Subclasses set this to register

# Access the auto-created registry
PLUGINS = PluginBase.__registry__

# Define plugins - they auto-register!
class MyPlugin(PluginBase):
    plugin_name = 'my_plugin'
    
    def run(self):
        return "Hello from my plugin!"

# Use the registry
print(list(PLUGINS.keys()))  # ['my_plugin']
plugin = PLUGINS['my_plugin']()
print(plugin.run())  # "Hello from my plugin!"
```

## Installation

```bash
pip install metaclass-registry
```

## Why metaclass-registry?

Most plugin systems require boilerplate code:

**Before** (Traditional approach):
```python
# Custom metaclass per registry
class PluginMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if hasattr(cls, 'plugin_name') and cls.plugin_name:
            PLUGINS[cls.plugin_name] = cls
        return cls

# Manual registry creation
PLUGINS = {}

# Base class with custom metaclass
class PluginBase(metaclass=PluginMeta):
    plugin_name = None
```

**After** (metaclass-registry):
```python
# Just class attributes!
class PluginBase(metaclass=AutoRegisterMeta):
    __registry_key__ = 'plugin_name'

# Access auto-created registry
PLUGINS = PluginBase.__registry__
```

## Advanced Features

### Registry Inheritance

```python
class BackendBase(metaclass=AutoRegisterMeta):
    __registry_key__ = 'backend_type'

class StorageBackend(BackendBase):
    pass  # Inherits BackendBase.__registry__

class ReadOnlyBackend(BackendBase):
    pass  # Also inherits BackendBase.__registry__

# All share the SAME registry!
assert StorageBackend.__registry__ is BackendBase.__registry__
```

### Secondary Registries

```python
METADATA_HANDLERS = {}

class MicroscopeHandler(metaclass=AutoRegisterMeta):
    __registry_key__ = 'microscope_type'
    __secondary_registries__ = [
        SecondaryRegistry(
            registry_dict=METADATA_HANDLERS,
            key_source=PRIMARY_KEY,
            attr_name='metadata_handler_class'
        )
    ]
```

### Custom Key Extractors

```python
def extract_key_from_suffix(cls):
    """Extract 'foo' from 'FooHandler'."""
    name = cls.__name__
    if name.endswith('Handler'):
        return name[:-7].lower()
    return None

class Handler(metaclass=AutoRegisterMeta):
    __registry_key__ = 'handler_type'
    __key_extractor__ = extract_key_from_suffix
```

## Documentation

Full documentation available at [metaclass-registry.readthedocs.io](https://metaclass-registry.readthedocs.io)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Credits

Developed by Tristan Simas as part of the OpenHCS project.
