from io import BytesIO
from typing import Any
import pytest

from cloud_storage import AsyncS3Storage


@pytest.mark.asyncio
async def test_s3_storage_methods(s3_test_env: Any):
    bucket_name, endpoint_without_scheme = s3_test_env

    storage = AsyncS3Storage(
        bucket_name=bucket_name,
        endpoint_url=endpoint_without_scheme,
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
        use_ssl=False,
    )

    file_content = b"hello moto"
    file_obj = BytesIO(file_content)

    key = "test/file.txt"

    # upload test
    returned_key = await storage.upload(file_obj, key)
    assert returned_key == storage.get_secure_key(key)

    # get url test without custom domain or querystring_auth
    url = await storage.get_url(key)
    assert key in url

    # get size test
    size = await storage.get_size(key)
    assert size == len(file_content)

    # delete test (should suceed silently)
    await storage.delete(key)

    # get size test after delete (should return 0)
    size_after_delete = await storage.get_size(key)
    assert size_after_delete == 0


@pytest.mark.asyncio
async def test_s3_storage_querystring_auth(s3_test_env: Any):
    bucket_name, endpoint_without_scheme = s3_test_env

    storage = AsyncS3Storage(
        bucket_name=bucket_name,
        endpoint_url=endpoint_without_scheme,
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
        use_ssl=False,
        querystring_auth=True,
    )

    key = "test/file.txt"
    url = await storage.get_url(key)

    assert url.count("AWSAccessKeyId=") == 1
    assert url.count("Signature=") == 1
    assert url.count("Expires=") == 1


@pytest.mark.asyncio
async def test_s3_storage_custom_domain(s3_test_env: Any):
    bucket_name, endpoint_without_scheme = s3_test_env

    storage = AsyncS3Storage(
        bucket_name=bucket_name,
        endpoint_url=endpoint_without_scheme,
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
        use_ssl=False,
        custom_domain="cdn.example.com",
    )

    key = "test/file.txt"
    url = await storage.get_url(key)

    assert url.startswith("http://cdn.example.com/")
    assert key in await storage.get_url(key)


@pytest.mark.asyncio
async def test_get_secure_key_normalization():
    storage = AsyncS3Storage(
        bucket_name="fake-bucket",
        endpoint_url="fake-endpoint-url",
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
        use_ssl=False,
    )

    raw_key = "../../weird ../file name.txt"
    normalized_key = storage.get_secure_key(raw_key)

    assert ".." not in normalized_key
    assert ".txt" in normalized_key
