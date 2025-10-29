# fastapi-cloud-storage

A powerful, extensible, and async-ready cloud object storage backend for FastAPI.

> Drop-in, plug-and-play cloud storage for your FastAPI apps; with full async support.\
Inspired by [fastapi-storages](https://github.com/aminalaee/fastapi-storages), built on modern async patterns using [aioboto3](https://github.com/terricain/aioboto3).

## Installation

```bash
uv add "fastapi-cloud-storage[s3]"
```

## Quick Start

1. **Define your async S3 storage**

```py
from async_storages import S3Storage

storage = S3Storage(
    bucket_name="your-bucket",
    endpoint_url="s3.your-cloud.com",
    aws_access_key_id="KEY",
    aws_secret_access_key="SECRET",
    # ...
)
```

2. **Define your SQLAlchemy/SQLModel model**\
   Use the provided `FileType` as the column type:

```py
from sqlalchemy import Column, Integer
from async_storages.integrations.sqlalchemy import FileType
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    file = Column(FileType(storage=storage))
```

3. **Upload files asynchronously before DB commit**\
   Since `SQLAlchemy` binding is `synchronous`, upload files explicitly before saving:

```py
# upload the file to storage before saving record
await storage.upload(file, file.name)

# then store the file name in the DB
doc = Document(file=file.name)
session.add(doc)
await session.commit()

# fetch from DB
doc = await session.get(Document, doc.id)
assert isinstance(doc.file, StorageFile)

url = await doc.file.get_url()
await doc.file.delete()
```

4. **Access files asynchronously**\
   When fetching from `DB`, file attribute is an `StorageFile` with async methods:

```py
doc = await session.get(Document, some_id)
doc_url = await doc.file.get_url()
doc_size = await doc.file.get_size()

await doc.file.upload(another_file)  # re-upload
await doc.file.delete()  # delete current file
```

## Example: FastAPI Integration

```py
from fastapi import FastAPI, UploadFile
from async_storages import S3Storage

app = FastAPI(...)
storage = S3Storage(...)

@app.post("/upload")
async def upload_file(file: UploadFile):
    name = await storage.upload(file.file, file.filename)
    return {"url": await storage.get_url(name)}
```

## License

[MIT](LICENSE) © 2025 ^_^ [`@stabldev`](https://github.com/stabldev)
