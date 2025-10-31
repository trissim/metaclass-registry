Quick Start Guide
=================

This guide will walk you through creating your first plugin registry with ``metaclass-registry``.

Installation
------------

Install via pip:

.. code-block:: bash

   pip install metaclass-registry

Basic Registry
--------------

Let's create a simple plugin system:

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta

   # Step 1: Define your base class
   class PluginBase(metaclass=AutoRegisterMeta):
       __registry_key__ = 'plugin_name'  # Attribute that contains the key
       plugin_name = None  # Subclasses will set this

   # Step 2: Access the auto-created registry
   PLUGINS = PluginBase.__registry__

   # Step 3: Create plugins
   class EmailPlugin(PluginBase):
       plugin_name = 'email'

       def send(self, message):
           print(f"Sending email: {message}")

   class SMSPlugin(PluginBase):
       plugin_name = 'sms'

       def send(self, message):
           print(f"Sending SMS: {message}")

   # Step 4: Use the registry
   print(list(PLUGINS.keys()))  # ['email', 'sms']

   # Get and use a plugin
   email_plugin = PLUGINS['email']()
   email_plugin.send("Hello!")  # Sending email: Hello!

Registry Inheritance
--------------------

Child classes automatically inherit the parent's registry:

.. code-block:: python

   class BaseBackend(metaclass=AutoRegisterMeta):
       __registry_key__ = 'backend_type'
       backend_type = None

   class StorageBackend(BaseBackend):
       """Storage-specific backend."""
       pass

   class ProcessingBackend(BaseBackend):
       """Processing-specific backend."""
       pass

   # Both share the same registry!
   assert StorageBackend.__registry__ is BaseBackend.__registry__
   assert ProcessingBackend.__registry__ is BaseBackend.__registry__

   class DiskStorage(StorageBackend):
       backend_type = 'disk'

   class MemoryStorage(StorageBackend):
       backend_type = 'memory'

   # All in the same registry
   print(list(BaseBackend.__registry__.keys()))  # ['disk', 'memory']

Custom Key Extraction
---------------------

Use a function to derive keys from class names:

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta, make_suffix_extractor

   class Handler(metaclass=AutoRegisterMeta):
       __registry_key__ = 'handler_type'
       __key_extractor__ = make_suffix_extractor('Handler')
       handler_type = None  # Optional when using extractor

   class ImageXpressHandler(Handler):
       pass  # handler_type will be 'imagexpress'

   class OperettaHandler(Handler):
       pass  # handler_type will be 'operetta'

   print(list(Handler.__registry__.keys()))  # ['imagexpress', 'operetta']

Skip Registration
-----------------

Control which classes get registered:

.. code-block:: python

   class OptionalPlugin(metaclass=AutoRegisterMeta):
       __registry_key__ = 'name'
       __skip_if_no_key__ = True  # Don't error if name is None
       name = None

   class RegisteredPlugin(OptionalPlugin):
       name = 'registered'  # Will be registered

   class UnregisteredPlugin(OptionalPlugin):
       pass  # name=None, will be skipped

   print(list(OptionalPlugin.__registry__.keys()))  # ['registered']

Secondary Registries
--------------------

Auto-populate related registries:

.. code-block:: python

   from metaclass_registry import SecondaryRegistry, PRIMARY_KEY

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

Next Steps
----------

* Learn about :doc:`patterns`
* Explore the :doc:`api`
* Check out more :doc:`examples`
