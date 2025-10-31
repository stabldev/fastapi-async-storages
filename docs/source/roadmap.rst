Roadmap
=======

This list shows the current and planned features of ``fastapi-async-storages``;
checked items are implemented, unchecked are upcoming.

Completed & Planned Features
-------------------------------

Storage Backends
~~~~~~~~~~~~~~~~
- [x] Async S3 backend powered by `aioboto3 <https://aioboto3.readthedocs.io/en/latest/>`_
- [x] Compatibility with `MinIO <https://min.io/>`_ and other S3-compatible services
- [ ] Async Local Filesystem backend using `aiofiles <https://github.com/Tinche/aiofiles>`_
- [ ] Async Google Cloud Storage (GCS) backend using `google-cloud-storage <https://googleapis.dev/python/storage/latest/index.html>`_
- [ ] Async Azure Blob Storage integration with `azure-sdk-for-python <https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python>`_

Framework Integrations
~~~~~~~~~~~~~~~~~~~~~~
- [x] `SQLAlchemy ORM <https://sqlalchemy.org/>`_ async integration
- [ ] `Tortoise ORM <https://tortoise-orm.readthedocs.io/en/latest/>`_ async integration
- [ ] `Peewee ORM <http://docs.peewee-orm.com/en/latest/peewee/async.html>`_ async integration

Features & Enhancements
~~~~~~~~~~~~~~~~~~~~~~~
- [x] Presigned URL generation for uploads and downloads
- [ ] Async streaming support for large files
- [ ] Bulk async upload and delete operations
- [ ] Progress tracking with hooks or callbacks
- [ ] Automatic cleanup utilities for orphaned/expired files

DX & Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- [x] Core documentation and usage examples
- [x] Testing utilities and mocks for async storage testing
- [ ] Expanded real-world usage and best practices
