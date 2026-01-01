from ._version import __version__ as __version__internal__
from .base import BaseStorage, StorageFile, StorageImage
from .s3 import S3Storage

__version__ = __version__internal__
__all__ = ["BaseStorage", "StorageFile", "StorageImage", "S3Storage"]
