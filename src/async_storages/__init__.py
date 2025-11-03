from .base import BaseStorage, StorageFile, StorageImage
from .s3 import S3Storage

__version__ = "0.1.1"
__all__ = ["BaseStorage", "StorageFile", "StorageImage", "S3Storage"]
