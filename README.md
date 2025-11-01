# fastapi-async-storages

A powerful, extensible, and async-ready cloud object storage backend for FastAPI.

> Drop-in, plug-and-play cloud storage for your FastAPI apps; with full async support.\
> Inspired by [fastapi-storages](https://github.com/aminalaee/fastapi-storages), built on modern async patterns using [aioboto3](https://github.com/terricain/aioboto3).

## Features

* Fully asynchronous storage interface designed for FastAPI applications
* Async S3 backend powered by [aioboto3](https://github.com/terricain/aioboto3)
* [SQLAlchemy](https://sqlalchemy.org/) and [SQLModel](https://sqlmodel.tiangolo.com/) integration
* Typed and extensible design
* Supports FastAPI dependency injection

## Installation

```bash
uv add fastapi-async-storages
# for s3 support:
uv add "fastapi-async-storages[s3]"
```

## Documentation

Full documentation is available on:\
https://fastapi-async-storages.readthedocs.io

## Example: FastAPI

```py
from fastapi import FastAPI, UploadFile
from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from async_storages import S3Storage
from async_storages.integrations.sqlalchemy import FileType

Base = declarative_base()

app = FastAPI()
storage = S3Storage(...)
engine = create_async_engine("sqlite+aiosqlite:///test.db", echo=True)

# create AsyncSession factory
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Example(Base):
    __tablename__ = "example"

    id = Column(Integer, primary_key=True)
    file = Column(FileType(storage=storage))

# create tables inside an async context
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/upload/")
async def create_upload_file(file: UploadFile):
    file_name = f"uploads/{file.filename}"
    # upload before commit due to the sqlalchemy binding being sync
    await storage.upload(file.file, file_name)

    example = Example(file=file)
    async with AsyncSessionLocal() as session:
        session.add(example)
        await session.commit()
        return {"filename": example.file.name}
```

## License

[MIT](LICENSE) © 2025 ^\_^ [`@stabldev`](https://github.com/stabldev)
