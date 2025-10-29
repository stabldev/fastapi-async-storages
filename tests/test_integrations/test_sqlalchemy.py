# pyright: reportOptionalMemberAccess=none
from io import BytesIO
from typing import Any
import pytest
from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import declarative_base

from async_storages import StorageFile
from async_storages.integrations.sqlalchemy import FileType

Base = declarative_base()


class Document(Base):
    __tablename__: str = "documents"
    id: Column[int] = Column(Integer, primary_key=True)
    file: Column[str] = Column(FileType(storage=None))  # pyright: ignore[reportArgumentType]


@pytest.mark.asyncio
async def test_sqlalchemy_with_s3(s3_test_storage: Any):
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

        # check instance type
        assert isinstance(doc.file, StorageFile)
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


@pytest.mark.asyncio
async def test_sqlalchemy_filetype_none_and_plain_string_with_s3(s3_test_storage: Any):
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

    # insert test records into db
    async with async_session() as session:
        # case 1: None value
        doc_none = Document(file=None)
        session.add(doc_none)

        # case 2: plain string value (simulate manually setting filename)
        doc_plain = Document(file="plain/path/file.txt")
        session.add(doc_plain)

        await session.commit()
        id_none, id_plain = doc_none.id, doc_plain.id

    # fetch records back and run tests
    async with async_session() as session:
        doc_none = await session.get(Document, id_none)
        doc_plain = await session.get(Document, id_plain)

        # None should stay None (no StorageFile instance)
        assert doc_none.file is None

        # check instance type
        assert isinstance(doc_plain.file, StorageFile)
        assert doc_plain.file.name == "plain/path/file.txt"

        # methods should work
        url = await doc_plain.file.get_url()
        assert "plain/path/file.txt" in url

    # close all connections
    await engine.dispose()
