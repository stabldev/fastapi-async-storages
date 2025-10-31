Usage
=====

This section provides practical examples and guidance on using ``fastapi-async-storages``
to handle asynchronous file storage in your FastAPI applications.

Working with storages
---------------------

Often in projects, you want to get input file in the API and store it somewhere.
The `fastapi-async-storages` simplifies the process to store and retrieve the files in a re-usable manner.

Available storage backends:

* :class:`~async_storages.S3Storage`: To store file objects in Amazon S3 or any s3-compatible object storage.

S3Storage
~~~~~~~~~

The :class:`~async_storages.S3Storage` class provides an asynchronous interface for interacting
with S3-compatible object storages such as AWS S3 or MinIO.

Now let's see a minimal example of using :class:`~async_storages.S3Storage` in action:

.. code-block:: python

  from io import BytesIO
  from async_storages import S3Storage

  storage = S3Storage(
    bucket_name="my-bucket",
    endpoint_url="localhost:9000", # no protocol (http/https)
    aws_access_key_id="fake-access-key",
    aws_secret_access_key="fake-secret-key",
    use_ssl=False,
  )

  async def main():
    file_name = "uploads/example.txt"
    file_obj = BytesIO(b"hello world")

    # upload a file
    await storage.upload(file_obj, file_name)
    # get file URL
    url = await storage.get_url(file_name)
    print(url)
    # get file size
    size = await storage.get_size(file_name)
    # delete file
    await storage.delete(file_name)

.. warning::

  You should never hard-code credentials like `aws_access_key_id` and `aws_secret_access_key` in the code.
  Instead, you can read values from environment variables or read from your app settings.

Working with ORM extensions
---------------------------

The example you saw was useful, but **fastapi-async-storages** has ORM integrations
which makes storing and serving the files easier.

Support ORM include:

* `SQLAlchemy <https://sqlalchemy.org>`_
* `SQLModel <https://sqlmodel.tiangolo.com>`_

SQLAlchemy
~~~~~~~~~~

You can use custom :code:`SQLAlchemy` types from :code:`fastapi-async-storages` for this.

Supported types include:

* :class:`~async_storages.integrations.sqlalchemy.FileType`: Type that returns a :class:`~async_storages.StorageFile` instance for file fields.
* :class:`~async_storages.integrations.sqlalchemy.ImageType`: Type that returns a :class:`~async_storages.StorageImage` instance for image fields.


Let's see an example:

.. code-block:: python

  from sqlalchemy import Column, Integer
  from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
  from sqlalchemy.ext.asyncio.session import async_sessionmaker
  from sqlalchemy.orm import declarative_base

  from async_storages import S3Storage
  from async_storages.integrations.sqlalchemy import FileType, ImageType

  Base = declarative_base()
  engine = create_async_engine("sqlite+aiosqlite:///:memory:")
  async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

  storage = S3Storage(
    bucket_name="my-bucket",
    endpoint_url="localhost:9000",
    aws_access_key_id="fake-access-key",
    aws_secret_access_key="fake-secret-key",
    use_ssl=False,
  )

  class Document(Base):
  __tablename__ = "documents"

  id = Column(Integer, primary_key=True)
  file = Column(FileType(storage=storage))
  image = Column(ImageType(storage=storage))

  async def main():
    async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)

  # create an in-memory image
  img_buf = BytesIO()
  Image.new("RGB", (32, 16), color=(255, 0, 0)).save(img_buf, format="PNG")
  img_buf.seek(0)

  # upload and link file and image
  img_name await storage.upload(img_buf, "uploads/test-image.png")
  file_name = await storage.upload(BytesIO(b"hello world"), "uploads/test.txt")

  async with async_session() as session:
    doc = Document(file=file_name, image=img_name)
    session.add(doc)
    await session.commit()

    doc = await session.get(Document, doc.id)
    url = await doc.file.get_url()
    print(url)
    width, height = await doc.image.get_dimensions()
    print(f"Dimensions: {width}x{height}")
