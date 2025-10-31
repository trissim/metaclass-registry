Examples
========

This page contains practical examples of using metaclass-registry.

Basic Plugin System
-------------------

Create a simple plugin system with auto-registration:

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta

   class PluginBase(metaclass=AutoRegisterMeta):
       __registry_key__ = 'plugin_name'
       plugin_name = None

       def execute(self):
           raise NotImplementedError

   class DataProcessor(PluginBase):
       plugin_name = 'processor'

       def execute(self):
           return "Processing data..."

   class DataValidator(PluginBase):
       plugin_name = 'validator'

       def execute(self):
           return "Validating data..."

   # Use the registry
   PLUGINS = PluginBase.__registry__
   for name, plugin_class in PLUGINS.items():
       plugin = plugin_class()
       print(f"{name}: {plugin.execute()}")

Microscope Handler System
--------------------------

Real-world example of a microscope handler registry with secondary registries:

.. code-block:: python

   from metaclass_registry import (
       AutoRegisterMeta,
       SecondaryRegistry,
       PRIMARY_KEY,
       make_suffix_extractor,
   )

   # Secondary registry for metadata handlers
   METADATA_HANDLERS = {}

   class MicroscopeHandler(metaclass=AutoRegisterMeta):
       __registry_key__ = 'microscope_type'
       __key_extractor__ = make_suffix_extractor('Handler')
       __secondary_registries__ = [
           SecondaryRegistry(
               registry_dict=METADATA_HANDLERS,
               key_source=PRIMARY_KEY,
               attr_name='metadata_handler_class'
           )
       ]
       microscope_type = None
       metadata_handler_class = None

       def read_image(self, path):
           raise NotImplementedError

   class ImageXpressMetadata:
       def parse(self, path):
           return {"vendor": "Molecular Devices"}

   class ImageXpressHandler(MicroscopeHandler):
       metadata_handler_class = ImageXpressMetadata

       def read_image(self, path):
           return f"Reading ImageXpress image from {path}"

   class OperettaMetadata:
       def parse(self, path):
           return {"vendor": "PerkinElmer"}

   class OperettaHandler(MicroscopeHandler):
       metadata_handler_class = OperettaMetadata

       def read_image(self, path):
           return f"Reading Operetta image from {path}"

   # Use the registries
   HANDLERS = MicroscopeHandler.__registry__
   print(list(HANDLERS.keys()))  # ['imagexpress', 'operetta']
   print(list(METADATA_HANDLERS.keys()))  # ['imagexpress', 'operetta']

   # Get a handler
   handler = HANDLERS['imagexpress']()
   print(handler.read_image('/path/to/image'))

Storage Backend System
----------------------

Example of a storage backend registry with inheritance:

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta

   class StorageBackend(metaclass=AutoRegisterMeta):
       __registry_key__ = 'backend_type'
       __skip_if_no_key__ = True
       backend_type = None

       def read(self, key):
           raise NotImplementedError

       def write(self, key, data):
           raise NotImplementedError

   class DiskStorage(StorageBackend):
       backend_type = 'disk'

       def read(self, key):
           return f"Reading {key} from disk"

       def write(self, key, data):
           return f"Writing {key} to disk"

   class MemoryStorage(StorageBackend):
       backend_type = 'memory'

       def __init__(self):
           self.store = {}

       def read(self, key):
           return self.store.get(key)

       def write(self, key, data):
           self.store[key] = data

   class ZarrStorage(StorageBackend):
       backend_type = 'zarr'

       def read(self, key):
           return f"Reading {key} from Zarr"

       def write(self, key, data):
           return f"Writing {key} to Zarr"

   # Factory function
   def get_storage(backend_type='disk'):
       BACKENDS = StorageBackend.__registry__
       backend_class = BACKENDS.get(backend_type)
       if not backend_class:
           raise ValueError(f"Unknown backend: {backend_type}")
       return backend_class()

   # Use the factory
   storage = get_storage('memory')
   storage.write('key1', 'value1')
   print(storage.read('key1'))

Custom Key Extractor
--------------------

Example of using custom key extraction logic:

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta

   def extract_version(class_name, cls):
       """Extract version from class name like 'V1Handler' -> 'v1'."""
       import re
       match = re.match(r'V(\d+)', class_name)
       if match:
           return f'v{match.group(1)}'
       return None

   class APIHandler(metaclass=AutoRegisterMeta):
       __registry_key__ = 'version'
       __key_extractor__ = extract_version
       version = None

       def handle_request(self, request):
           raise NotImplementedError

   class V1Handler(APIHandler):
       def handle_request(self, request):
           return f"V1: {request}"

   class V2Handler(APIHandler):
       def handle_request(self, request):
           return f"V2: {request}"

   class V3Handler(APIHandler):
       def handle_request(self, request):
           return f"V3: {request}"

   # Route based on version
   HANDLERS = APIHandler.__registry__
   print(list(HANDLERS.keys()))  # ['v1', 'v2', 'v3']

   def route_request(version, request):
       handler_class = HANDLERS.get(version)
       if not handler_class:
           raise ValueError(f"Unsupported API version: {version}")
       handler = handler_class()
       return handler.handle_request(request)

   print(route_request('v2', 'GET /users'))  # V2: GET /users

Multi-Level Inheritance
-----------------------

Example showing registry inheritance across multiple levels:

.. code-block:: python

   from metaclass_registry import AutoRegisterMeta

   class BaseProcessor(metaclass=AutoRegisterMeta):
       __registry_key__ = 'name'
       name = None

   class ImageProcessor(BaseProcessor):
       """All image processors share the same registry."""
       pass

   class VideoProcessor(BaseProcessor):
       """All video processors share the same registry."""
       pass

   class JPEGProcessor(ImageProcessor):
       name = 'jpeg'

       def process(self, data):
           return "Processing JPEG"

   class PNGProcessor(ImageProcessor):
       name = 'png'

       def process(self, data):
           return "Processing PNG"

   class MP4Processor(VideoProcessor):
       name = 'mp4'

       def process(self, data):
           return "Processing MP4"

   # All share the same registry
   assert ImageProcessor.__registry__ is BaseProcessor.__registry__
   assert VideoProcessor.__registry__ is BaseProcessor.__registry__

   # All processors in one place
   PROCESSORS = BaseProcessor.__registry__
   print(list(PROCESSORS.keys()))  # ['jpeg', 'png', 'mp4']
