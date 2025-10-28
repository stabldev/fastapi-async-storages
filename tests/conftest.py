from typing import Any
import pytest


@pytest.fixture
async def s3_test_env(aioboto3_s3_client: Any) -> tuple[str, str]:
    bucket_name = "test-bucket"
    await aioboto3_s3_client.create_bucket(Bucket=bucket_name)

    endpoint_url_with_protocol = str(aioboto3_s3_client.meta.endpoint_url)
    endpoint_url = endpoint_url_with_protocol.replace("http://", "")

    return bucket_name, endpoint_url
