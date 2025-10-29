from io import BytesIO
from typing import Any
import pytest
from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import declarative_base

from cloud_storage import AsyncStorageFile
from cloud_storage.integrations.sqlalchemy import AsyncFileType

Base = declarative_base()


class Document(Base):
    __tablename__: str = "documents"
    id: Column[int] = Column(Integer, primary_key=True)
    file: Column[str] = Column(AsyncFileType(storage=None))  # pyright: ignore[reportArgumentType]


@pytest.mark.asyncio
async def test_sqlalchemy_filetype_with_s3(s3_test_storage: Any):
    storage = s3_test_storage
    # assign s3_storage to file column
    Document.__table__.columns.file.type.storage = storage

    # create async engine and session
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # create db tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # create demo file object
    file_name = "uploads/test-file.txt"
    file_content = b"SQLAlchemy + S3 integration test"
    file_obj = BytesIO(file_content)

    # upload to s3 storage to fetch from db and test methods
    await storage.upload(file_obj, file_name)

    # insert record into db
    async with async_session() as session:
        doc = Document(file=file_name)
        session.add(doc)
        await session.commit()
        doc_id = doc.id

    # fetch record back and run tests
    async with async_session() as session:
        doc = await session.get(Document, doc_id)
        if doc is None:
            return

        # check instance type
        assert isinstance(doc.file, AsyncStorageFile)
        assert doc.file.name == f"{file_name}"

        # methods should work
        url = await doc.file.get_url()
        assert file_name in url

        size = await doc.file.get_size()
        assert size == len(file_content)

        # deleting should not raise
        await doc.file.delete()
        size_after_delete = await storage.get_size(file_name)
        assert size_after_delete == 0

    # close all connections
    await engine.dispose()
