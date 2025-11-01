metaclass-registry Documentation
==================================

**Zero-boilerplate metaclass-driven plugin registry system with lazy discovery and caching**

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   api
   examples
   patterns

Overview
--------

``metaclass-registry`` is a Python library that provides a reusable metaclass infrastructure for creating automatic plugin registration systems. It eliminates the need for custom metaclasses and manual registry management by providing a configuration-driven approach that works out of the box.

Key Features
------------

* **Zero Boilerplate**: No custom metaclasses, no manual registry creation, just class attributes
* **Lazy Discovery**: Plugins discovered automatically on first access
* **Registry Inheritance**: Child classes inherit parent's registry for clean interface hierarchies
* **Secondary Registries**: Auto-populate related registries from primary registry
* **Persistent Caching**: Cache discovery results across process restarts
* **Auto-Configuration**: Automatic inference of discovery packages and recursive settings
* **Type-Safe**: Full type hints and mypy support

Installation
------------

.. code-block:: bash

   pip install metaclass-registry

Quick Example
-------------

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta

   # Define a base class with registry configuration
   class PluginBase(metaclass=AutoRegisterMeta):
       __registry_key__ = 'plugin_name'
       plugin_name = None

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
