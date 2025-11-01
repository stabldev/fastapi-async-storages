FAQ
===

This section answers common questions about ``fastapi-async-storages``, explaining its purpose,
differences from similar libraries, usage considerations, and extensibility options.

What is `fastapi-async-storages <https://github.com/stabldev/fastapi-async-storages>`_?
---------------------------------------------------------------------------------------
`fastapi-async-storages <https://github.com/stabldev/fastapi-async-storages>`_ is the asynchronous counterpart to `fastapi-storages <https://github.com/aminalaee/fastapi-storages>`_.
It provides non-blocking storage backends for FastAPI applications using async libraries such as `aioboto3 <https://aioboto3.readthedocs.io/en/latest/usage.html>`_ for S3.

How is it different from `fastapi-storages <https://github.com/aminalaee/fastapi-storages>`_?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
While `fastapi-storages <https://github.com/aminalaee/fastapi-storages>`_ is sync-based and built around traditional blocking I/O,
`fastapi-async-storages <https://github.com/stabldev/fastapi-async-storages>`_ is fully asynchronous.
This allows your FastAPI app to handle more concurrent requests efficiently, especially during file upload or download operations.

Why upload files before commit?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
`SQLAlchemy <https://sqlalchemy.org>`_’s ORM is primarily synchronous, even when used with `AsyncSession <https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html>`_.
The model layer and column bindings (including file fields) are not async-aware.
Therefore, storage operations like uploading or deleting files must happen **before** the database commit.

Does `SQLModel <https://sqlmodel.tiangolo.com/>`_ integration work the same way?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Yes. The `SQLModel <https://sqlmodel.tiangolo.com/>`_ integration layer internally uses `SQLAlchemy <https://sqlalchemy.org>`_’s async engine and sessions.
You can define :class:`~async_storages.integrations.sqlalchemy.FileType` columns exactly as you would in SQLAlchemy models, following the same upload-before-commit pattern.

Can I use it in synchronous contexts?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can, but it’s not recommended. The library is designed around `asyncio <https://docs.python.org/3/library/asyncio.html>`_ to take advantage of FastAPI’s asynchronous execution.
If your app runs entirely synchronously, stick with `fastapi-storages <https://github.com/aminalaee/fastapi-storages>`_ for simplicity.

Can I extend it with other storage backends?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Yes. The library’s base :class:`~async_storages.base.BaseStorage` class is extensible.
You can implement new async backends (like local filesystem, Google Cloud Storage, or Azure Blob) by subclassing it and implementing the async methods ``upload``, ``get_path``, and ``delete``.

`fastapi-async-storages <https://github.com/stabldev/fastapi-async-storages>`_ aims to stay compatible with existing `fastapi-storages <https://github.com/aminalaee/fastapi-storages>`_ APIs, so extension patterns remain familiar.
