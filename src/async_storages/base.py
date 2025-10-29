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
    """
    File object managed by a storage backend.

    :param name: The name or identifier of the stored file.
    :type name: str
    :param storage: The storage backend handling file operations.
    :type storage: BaseStorage
    """

    def __init__(self, name: str, storage: BaseStorage):
        self._name: str = name
        self._storage: BaseStorage = storage

    @property
    def name(self) -> str:
        """
        Get the name of the file.

        :return: The name of the file in storage.
        :rtype: str
        """
        return self._name

    async def get_size(self) -> int:
        """
        Get the size of the file in bytes.

        :return: The file size in bytes.
        :rtype: int
        """
        return await self._storage.get_size(self._name)

    async def get_url(self) -> str:
        """
        Get a URL or path to access the file.

        :return: A URL or file path string.
        :rtype: str
        """
        return await self._storage.get_url(self._name)

    async def upload(self, file: BinaryIO) -> str:
        """
        Upload a file to the storage backend.

        :param file: A binary file-like object to upload.
        :type file: BinaryIO
        :return: The name or path of the uploaded file.
        :rtype: str
        """
        return await self._storage.upload(file=file, name=self._name)

    async def delete(self) -> None:
        """
        Delete the file from the storage backend.

        :return: None
        :rtype: None
        """
        await self._storage.delete(self._name)


class StorageImage(StorageFile):
    """
    Image file object managed by a storage backend.
    Extends :class:`StorageFile` by including optional image metadata such as width and height.

    :param name: The name or identifier of the stored image file.
    :type name: str
    :param storage: The storage backend handling file operations.
    :type storage: BaseStorage
    :param width: The width of the image in pixels.
    :type width: int
    :param height: The height of the image in pixels.
    :type height: int
    """

    def __init__(self, name: str, storage: BaseStorage, width: int, height: int):
        super().__init__(name, storage)
        self._width: int = width
        self._height: int = height

    @property
    def width(self) -> int:
        """
        Get the width of the image in pixels.

        :return: The image width in pixels.
        :rtype: int
        """
        return self._width

    @property
    def height(self) -> int:
        """
        Get the height of the image in pixels.

        :return: The image height in pixels.
        :rtype: int
        """
        return self._height
