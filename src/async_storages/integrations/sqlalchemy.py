from typing import Any, override
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import TypeDecorator, TypeEngine, Unicode

from async_storages.base import BaseStorage, StorageFile


class FileType(TypeDecorator[Any]):
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

        name = getattr(value, "name", None)
        if name:
            return name
        return str(value)

    @override
    def process_result_value(
        self, value: Any | None, dialect: Dialect
    ) -> StorageFile | None:
        if value is None:
            return None
        return StorageFile(name=value, storage=self.storage)
