from typing import Any, override
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import TypeDecorator, TypeEngine, Unicode

from async_storages.base import BaseStorage, StorageFile


class FileType(TypeDecorator[Any]):
    """
    SQLAlchemy column type for representing stored files.

    This type integrates with :class:`~async_storages.base.BaseStorage`
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
        """
        Process the Python value before storing it in the database.

        Converts :class:`~async_storages.StorageFile` objects
        (or similar objects with a ``name`` attribute) into their
        string name representation for persistence.

        :param value: The Python value being bound to a database column.
        :type value: Any
        :param dialect: The SQLAlchemy database dialect in use.
        :type dialect: Dialect
        :return: The serialized string representation of the file name.
        :rtype: str
        """
        if value is None:
            return value
        if isinstance(value, str):
            return value

        name = getattr(value, "name", None)
        if name:
            return name
        return str(value)

    @override
    def process_result_value(
        self, value: Any | None, dialect: Dialect
    ) -> StorageFile | None:
        """
        Process the database value after fetching from the database.

        Converts a stored file name string into a
        :class:`~async_storages.StorageFile` instance
        associated with the configured storage backend.

        :param value: The raw value retrieved from the database.
        :type value: Any or None
        :param dialect: The SQLAlchemy database dialect in use.
        :type dialect: Dialect
        :return: A :class:`~async_storages.StorageFile` instance, or ``None``.
        :rtype: StorageFile or None
        """
        if value is None:
            return None
        return StorageFile(name=value, storage=self.storage)
