Registry Patterns
=================

This guide explains different registry patterns and when to use each one.

Pattern A: Metaclass Registry (AutoRegisterMeta)
-------------------------------------------------

**Use AutoRegisterMeta when:**

* 1:1 mapping between classes and plugins
* Automatic discovery and registration needed
* Registration happens at class definition time
* Simple metadata (just a key and maybe one secondary registry)

Example
~~~~~~~

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta

   class MicroscopeHandler(metaclass=AutoRegisterMeta):
       __registry_key__ = 'microscope_type'
       microscope_type = None

   class ImageXpressHandler(MicroscopeHandler):
       microscope_type = 'imagexpress'

   HANDLERS = MicroscopeHandler.__registry__

Advantages
~~~~~~~~~~

* Zero boilerplate
* Automatic registration
* Type-safe with mypy
* Registry inheritance

Disadvantages
~~~~~~~~~~~~~

* Limited to 1:1 class-to-plugin mapping
* Less flexible than manual registration

Pattern B: Service Pattern
---------------------------

**Use Service Pattern when:**

* Many-to-one mapping (multiple items per plugin)
* Complex metadata (8+ fields)
* Need aggregation across multiple sources
* Dynamic registration after class creation

Example
~~~~~~~

.. code-block:: python

   # Not provided by metaclass-registry
   # Use manual registration with dataclasses for metadata
   from dataclasses import dataclass
   from typing import Dict, Callable

   @dataclass
   class FunctionMetadata:
       name: str
       category: str
       library: str
       function: Callable
       # ... more fields

   FUNCTIONS: Dict[str, FunctionMetadata] = {}

   def register_function(metadata: FunctionMetadata):
       FUNCTIONS[metadata.name] = metadata

Pattern C: Functional Registry
-------------------------------

**Use Functional Registry when:**

* Simple type-to-handler mappings
* No state needed
* Functional programming style preferred
* Very simple use cases

Example
~~~~~~~

.. code-block:: python

   # Simple dict for type mappings
   TYPE_HANDLERS = {
       'int': int_handler,
       'str': str_handler,
       'float': float_handler,
   }

Pattern D: Manual Registration
-------------------------------

**Use Manual Registration when:**

* Complex initialization logic required
* Explicit control over registration timing needed
* Very few plugins (< 3)
* Registration happens after class creation

Example
~~~~~~~

.. code-block:: python

   SERVERS = {}

   class ZMQServer:
       def __init__(self, config):
           self.config = config

   # Manual registration after initialization
   server = ZMQServer(config)
   SERVERS['zmq'] = server

Comparison Table
----------------

.. list-table::
   :header-rows: 1
   :widths: 20 30 15 15

   * - Pattern
     - Use Case
     - Complexity
     - Boilerplate
   * - A: AutoRegisterMeta
     - Simple 1:1 class plugins
     - Low
     - None
   * - B: Service Pattern
     - Complex metadata, many-to-one
     - Medium
     - Medium
   * - C: Functional
     - Simple type mappings
     - Very Low
     - None
   * - D: Manual
     - Complex initialization
     - Medium
     - High

Advanced Pattern A Features
----------------------------

Secondary Registries
~~~~~~~~~~~~~~~~~~~~

Auto-populate related registries:

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta, SecondaryRegistry, PRIMARY_KEY

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
       microscope_type = None
       metadata_handler_class = None

   class ImageXpressHandler(MicroscopeHandler):
       microscope_type = 'imagexpress'
       metadata_handler_class = ImageXpressMetadata

   # Primary registration
   print(MicroscopeHandler.__registry__)  # {'imagexpress': ImageXpressHandler}

   # Secondary registration
   print(METADATA_HANDLERS)  # {'imagexpress': ImageXpressMetadata}

Custom Key Extractors
~~~~~~~~~~~~~~~~~~~~~~

Derive keys from class names:

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta

   def extract_microscope_key(class_name, cls):
       """Extract 'foo' from 'FooHandler'."""
       if class_name.endswith('Handler'):
           return class_name[:-7].lower()
       return None

   class Handler(metaclass=AutoRegisterMeta):
       __registry_key__ = 'handler_type'
       __key_extractor__ = extract_microscope_key
       handler_type = None

   class ImageXpressHandler(Handler):
       pass  # Automatically registered as 'imagexpress'

Registry Caching
~~~~~~~~~~~~~~~~

Automatically cache discovered plugins:

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta, LazyDiscoveryDict

   # Enable caching (default)
   class Plugin(metaclass=AutoRegisterMeta):
       __registry_key__ = 'name'

   # Disable caching
   registry = LazyDiscoveryDict(enable_cache=False)
   # ... use in RegistryConfig

Migration Guide
---------------

From Custom Metaclass to AutoRegisterMeta
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before:**

.. code-block:: python

   class MyPluginMeta(type):
       def __new__(mcs, name, bases, attrs):
           cls = super().__new__(mcs, name, bases, attrs)
           if hasattr(cls, 'plugin_name') and cls.plugin_name:
               PLUGINS[cls.plugin_name] = cls
           return cls

   PLUGINS = {}

   class PluginBase(metaclass=MyPluginMeta):
       plugin_name = None

**After:**

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta

   class PluginBase(metaclass=AutoRegisterMeta):
       __registry_key__ = 'plugin_name'
       plugin_name = None

   PLUGINS = PluginBase.__registry__

Best Practices
--------------

1. **Use Pattern A for most plugin systems** - It handles 90% of use cases
2. **Choose explicit keys over extractors** - More maintainable
3. **Enable caching for production** - Faster startup times
4. **Use registry inheritance** - Clean hierarchies
5. **Document your registry structure** - Help users understand the system
