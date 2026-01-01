from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("async_storages")
except PackageNotFoundError:
    __version__ = "dev"
