from typing import Any, override
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import TypeDecorator, TypeEngine, Unicode

from cloud_storage.base import AsyncBaseStorage, AsyncStorageFile


class AsyncFileType(TypeDecorator[Any]):
    impl: TypeEngine[Any] | type[TypeEngine[Any]] = Unicode
    cache_ok: bool | None = True

    def __init__(self, storage: AsyncBaseStorage, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.storage: AsyncBaseStorage = storage

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
    ) -> AsyncStorageFile | None:
        if value is None:
            return None
        return AsyncStorageFile(name=value, storage=self.storage)
