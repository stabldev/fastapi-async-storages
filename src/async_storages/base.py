# pyright: reportUnusedParameter=none
from abc import ABC, abstractmethod
import asyncio
from io import BytesIO
from PIL import Image
from typing import BinaryIO


class BaseStorage(ABC):
    """
    Abstract base class defining the interface for storage backends.

    Subclasses must implement all methods to provide storage operations
    such as file upload, deletion, and retrieval of metadata or URLs.
    """

    @abstractmethod
    def get_name(self, name: str) -> str:
        """
        Get the name of the file.

        :param name: Original file name or identifier.
        :type name: str
        :return: The name of the file in storage.
        :rtype: str
        """
        pass

    @abstractmethod
    async def get_size(self, name: str) -> int:
        """
        Get the size of the file in bytes.

        :param name: Original file name or identifier.
        :type name: str
        :return: The file size in bytes.
        :rtype: int
        """
        pass

    @abstractmethod
    async def get_url(self, name: str) -> str:
        """
        Get a URL or path to access the file.

        :param name: Original file name or identifier.
        :type name: str
        :return: A URL or file path string.
        :rtype: str
        """
        pass

    @abstractmethod
    async def open(self, name: str) -> BytesIO:
        """
        Open an object and return it as an in-memory binary stream.

        :param name: Original file name or identifier.
        :type name: str
        :return: A BytesIO object containing the file's contents.
        :rtype: BytesIO
        """
        pass

    @abstractmethod
    async def upload(self, file: BinaryIO, name: str) -> str:
        """
        Upload a file to the storage backend.

        :param file: A binary file-like object to upload.
        :type file: BinaryIO
        :param name: Original file name or identifier.
        :type name: str
        :return: The name or path of the uploaded file.
        :rtype: str
        """
        pass

    @abstractmethod
    async def delete(self, name: str) -> None:
        """
        Delete the file from the storage backend.

        :param name: Original file name or identifier.
        :type name: str
        :return: None
        :rtype: None
        """
        pass


class StorageFile:
    """
    File object managed by a storage backend.

    :param name: The name or identifier of the stored file.
    :type name: str
    :param storage: The storage backend handling file operations.
    :type storage: BaseStorage
    """

    def __init__(self, name: str, storage: BaseStorage) -> None:
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
    :param width: The width of the image in pixels. Defaults to ``0`` if unknown.
    :type width: int, optional
    :param height: The height of the image in pixels. Defaults to ``0`` if unknown.
    :type height: int
    """

    def __init__(
        self, name: str, storage: BaseStorage, width: int = 0, height: int = 0
    ) -> None:
        super().__init__(name, storage)
        self._width: int = width
        self._height: int = height
        self._meta_loaded: bool = bool(width and height)

    async def _load_meta(self) -> None:
        data = await self._storage.open(self.name)

        def _extract_meta() -> tuple[int, int]:
            with Image.open(data) as image:
                return image.size

        self._width, self._height = await asyncio.to_thread(_extract_meta)
        self._meta_loaded = True

    async def get_dimensions(self) -> tuple[int, int]:
        """
        Retrieve the dimensions of the image (width and height).

        If the image metadata has not been loaded yet, this method asynchronously
        loads it from the storage backend before returning the values.

        :return: A tuple containing the image width and height in pixels.
        :rtype: tuple[int, int]
        :raises OSError: If the image file cannot be opened or read from storage.
        :raises ValueError: If the image file is not a valid image or dimensions cannot be determined.
        """
        if not self._meta_loaded:
            await self._load_meta()
        return self._width, self._height
