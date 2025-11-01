from io import BytesIO
from typing import Any
import pytest

from async_storages import S3Storage


@pytest.mark.asyncio
async def test_s3_storage_methods(s3_test_env: Any):
    bucket_name, endpoint_without_scheme = s3_test_env
    storage = S3Storage(
        bucket_name=bucket_name,
        endpoint_url=endpoint_without_scheme,
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
        use_ssl=False,
    )

    file_name = "test/file.txt"
    file_content = b"hello moto"
    file_obj = BytesIO(file_content)

    # upload test
    returned_name = await storage.upload(file_obj, file_name)
    assert returned_name == storage.get_name(file_name)

    # get url test without custom domain or querystring_auth
    path = await storage.get_path(file_name)
    assert file_name in path

    # get size test
    size = await storage.get_size(file_name)
    assert size == len(file_content)

    # delete test (should suceed silently)
    await storage.delete(file_name)

    # get size test after delete (should return 0)
    size_after_delete = await storage.get_size(file_name)
    assert size_after_delete == 0


@pytest.mark.asyncio
async def test_s3_storage_querystring_auth(s3_test_env: Any):
    bucket_name, endpoint_without_scheme = s3_test_env

    storage = S3Storage(
        bucket_name=bucket_name,
        endpoint_url=endpoint_without_scheme,
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
        use_ssl=False,
        querystring_auth=True,
    )

    name = "test/file.txt"
    path = await storage.get_path(name)

    assert path.count("AWSAccessKeyId=") == 1
    assert path.count("Signature=") == 1
    assert path.count("Expires=") == 1


@pytest.mark.asyncio
async def test_s3_storage_custom_domain(s3_test_env: Any):
    bucket_name, endpoint_without_scheme = s3_test_env

    storage = S3Storage(
        bucket_name=bucket_name,
        endpoint_url=endpoint_without_scheme,
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
        use_ssl=False,
        custom_domain="cdn.example.com",
    )

    name = "test/file.txt"
    path = await storage.get_path(name)

    assert path.startswith("http://cdn.example.com/")
    assert name in await storage.get_path(name)


@pytest.mark.asyncio
async def test_get_secure_key_normalization():
    storage = S3Storage(
        bucket_name="fake-bucket",
        endpoint_url="fake-endpoint-url",
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
        use_ssl=False,
    )

    raw_name = "../../weird ../file name.txt"
    normalized_name = storage.get_name(raw_name)

    assert ".." not in normalized_name
    assert ".txt" in normalized_name
