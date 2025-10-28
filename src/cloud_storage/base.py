# pyright: reportUnusedParameter=none
from typing import BinaryIO


class AsyncBaseStorage:
    def get_secure_key(self, key: str) -> str:
        raise NotImplementedError()

    async def get_size(self, key: str) -> int:
        raise NotImplementedError()

    async def get_url(self, key: str) -> str:
        raise NotImplementedError()

    async def upload(self, file: BinaryIO, key: str) -> str:
        raise NotImplementedError()

    async def delete(self, key: str) -> None:
        raise NotImplementedError()
