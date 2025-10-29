from typing import Any
import pytest

from async_storages import S3Storage


@pytest.fixture
async def s3_test_storage(s3_test_env: Any) -> S3Storage:
    bucket_name, endpoint_without_scheme = s3_test_env

    return S3Storage(
        bucket_name=bucket_name,
        endpoint_url=endpoint_without_scheme,
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
        use_ssl=False,
    )
