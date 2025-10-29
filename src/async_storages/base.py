# pyright: reportUnusedParameter=none
from typing import BinaryIO


class BaseStorage:
    def get_name(self, name: str) -> str:
        raise NotImplementedError()

    async def get_size(self, name: str) -> int:
        raise NotImplementedError()

    async def get_url(self, name: str) -> str:
        raise NotImplementedError()

    async def upload(self, file: BinaryIO, name: str) -> str:
        raise NotImplementedError()

    async def delete(self, name: str) -> None:
        raise NotImplementedError()


class StorageFile:
    def __init__(self, name: str, storage: BaseStorage):
        self._name: str = name
        self._storage: BaseStorage = storage

    @property
    def name(self) -> str:
        return self._name

    async def get_size(self) -> int:
        return await self._storage.get_size(self._name)

    async def get_url(self) -> str:
        return await self._storage.get_url(self._name)

    async def upload(self, file: BinaryIO) -> str:
        return await self._storage.upload(file=file, name=self._name)

    async def delete(self) -> None:
        await self._storage.delete(self._name)
