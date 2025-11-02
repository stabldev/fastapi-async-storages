from typing import Any, override
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import TypeDecorator, TypeEngine, Unicode

from async_storages import StorageFile, StorageImage
from async_storages.base import BaseStorage


class FileType(TypeDecorator[Any]):
    """
    SQLAlchemy column type for representing stored files.

    This type integrates with :class:`~async_storages.BaseStorage`
    to automatically wrap database values (file names) into
    :class:`~async_storages.StorageFile` objects when queried.

    :param storage: The storage backend used to manage file operations.
    :type storage: BaseStorage
    :param args: Additional positional arguments passed to ``TypeDecorator``.
    :param kwargs: Additional keyword arguments passed to ``TypeDecorator``.
    """

    impl: TypeEngine[Any] | type[TypeEngine[Any]] = Unicode
    cache_ok: bool | None = True

    def __init__(self, storage: BaseStorage, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.storage: BaseStorage = storage

    @override
    def process_bind_param(self, value: Any, dialect: Dialect) -> str:
        if value is None:
            return value
        if isinstance(value, str):
            return value

        filename = getattr(value, "filename", None)
        if filename:
            return filename
        return str(value)

    @override
    def process_result_value(
        self, value: Any | None, dialect: Dialect
    ) -> StorageFile | None:
        if value is None:
            return None
        return StorageFile(name=value, storage=self.storage)


class ImageType(FileType):
    """
    SQLAlchemy column type for representing stored image files.

    This type extends :class:`~.FileType` to automatically wrap
    database values (image file names) into
    :class:`~async_storages.StorageImage` objects when queried.

    It integrates with a configured :class:`~async_storages.BaseStorage`
    backend to provide convenient access to image operations such as
    resizing, thumbnail generation, or metadata retrieval.

    :param storage: The storage backend used to manage image file operations.
    :type storage: BaseStorage
    :param args: Additional positional arguments passed to ``FileType``.
    :param kwargs: Additional keyword arguments passed to ``FileType``.
    """

    @override
    def process_result_value(
        self, value: Any | None, dialect: Dialect
    ) -> StorageImage | None:
        if value is None:
            return None
        return StorageImage(name=value, storage=self.storage)
