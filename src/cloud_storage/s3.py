# pyright: reportPrivateLocalImportUsage=none
import mimetypes
from pathlib import Path
from typing import Any, BinaryIO, override

from cloud_storage.base import AsyncBaseStorage
from cloud_storage.utils import secure_filename

try:
    import aioboto3
    from botocore.exceptions import ClientError
except ImportError:
    raise ImportError(
        "'aioboto3' is not installed. Install with 'fastapi-cloud-storage[s3]'."
    )


class AsyncS3Storage(AsyncBaseStorage):
    def __init__(
        self,
        bucket_name: str,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str | None = None,
        use_ssl: bool = True,
        default_acl: str | None = None,
        custom_domain: str | None = None,
        querystring_auth: bool = False,
    ):
        assert not endpoint_url.startswith("http"), (
            "Endpoint should not contain protocol"
        )

        self.bucket_name: str = bucket_name
        self.endpoint_url: str = endpoint_url.rstrip("/")
        self.aws_access_key_id: str = aws_access_key_id
        self.aws_secret_access_key: str = aws_secret_access_key
        self.region_name: str | None = region_name
        self.use_ssl: bool = use_ssl
        self.default_acl: str | None = default_acl
        self.custom_domain: str | None = custom_domain
        self.querystring_auth: bool = querystring_auth

        self._http_scheme: str = "https" if self.use_ssl else "http"
        self._url: str = f"{self._http_scheme}://{self.endpoint_url}"
        self._session: "aioboto3.Session" = aioboto3.Session()

    def _get_s3_client(self) -> Any:
        return self._session.client(
            "s3",
            region_name=self.region_name,
            use_ssl=self.use_ssl,
            endpoint_url=self._url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

    @override
    def get_secure_key(self, key: str) -> str:
        parts = Path(key).parts
        safe_parts: list[str] = []

        for part in parts:
            if part not in ("..", ".", ""):
                safe_parts.append(secure_filename(part))

        safe_path = Path(*safe_parts)
        return str(safe_path)

    @override
    async def get_size(self, key: str) -> int:
        key = self.get_secure_key(key)

        async with self._get_s3_client() as s3_client:
            try:
                response = await s3_client.head_object(Bucket=self.bucket_name, Key=key)
                return int(response.get("ContentLength", 0))
            except ClientError as e:
                code = e.response.get("Error", {}).get("Code")
                status = e.response.get("ResponseMetadata", {}).get("HTTPStatusCode")

                if code in ("NoSuchKey", "NotFound") or status == 404:
                    return 0
                raise

    @override
    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        if self.custom_domain:
            return f"{self._http_scheme}://{self.custom_domain}/{key}"
        elif self.querystring_auth:
            async with self._get_s3_client() as s3_client:
                params = {"Bucket": self.bucket_name, "Key": key}
                return await s3_client.generate_presigned_url(
                    "get_object", Params=params, ExpiresIn=expires_in
                )
        else:
            url = f"{self._http_scheme}://{self.endpoint_url}/{self.bucket_name}/{key}"
            return url

    @override
    async def upload(self, file: BinaryIO, key: str) -> str:
        key = self.get_secure_key(key)
        content_type, _ = mimetypes.guess_type(key)
        extra_args = {"ContentType": content_type or "application/octet-stream"}
        if self.default_acl:
            extra_args["ACL"] = self.default_acl

        async with self._get_s3_client() as s3_client:
            file.seek(0)
            await s3_client.put_object(
                Bucket=self.bucket_name, Key=key, Body=file, **extra_args
            )
        return key

    @override
    async def delete(self, key: str) -> None:
        async with self._get_s3_client() as s3_client:
            try:
                await s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") != "NoSuchKey":
                    raise
