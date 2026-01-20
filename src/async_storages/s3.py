from io import BytesIO
import mimetypes
from pathlib import PurePosixPath
from typing import Any, BinaryIO, override

from async_storages.base import BaseStorage
from async_storages.utils import secure_filename

try:
    import aioboto3
    from botocore.exceptions import ClientError
except ImportError:
    raise ImportError(
        "'aioboto3' is not installed. Install with 'fastapi-async-storages[s3]'."
    )


class S3Storage(BaseStorage):
    """
    Asynchronous storage backend for Amazon S3-compatible object storage.

    This class provides async methods for uploading, retrieving, and deleting files
    in an S3 bucket using the ``aioboto3`` client.

    :param bucket_name: Name of the S3 bucket.
    :type bucket_name: str
    :param endpoint_url: The S3 endpoint hostname (without protocol).
    :type endpoint_url: str
    :param aws_access_key_id: AWS access key ID for authentication.
    :type aws_access_key_id: str
    :param aws_secret_access_key: AWS secret access key for authentication.
    :type aws_secret_access_key: str
    :param region_name: AWS region name (optional).
    :type region_name: str or None
    :param use_ssl: Whether to use HTTPS (True) or HTTP (False).
    :type use_ssl: bool
    :param default_acl: Default Access Control List (ACL) to apply when uploading files.
    :type default_acl: str or None
    :param custom_domain: Custom domain for serving files (e.g. CDN).
    :type custom_domain: str or None
    :param querystring_auth: Whether to generate presigned URLs with query parameters.
    :type querystring_auth: bool
    :raises ImportError: If ``aioboto3`` is not installed.
    """

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
    ) -> None:
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
    def get_name(self, name: str) -> str:
        """
        Sanitize and normalize a file path before uploading to S3.

        Removes unsafe path components (``..`` or ``.``) and ensures each
        segment is a secure filename.

        :param name: Original file name or path.
        :type name: str
        :return: Sanitized file path.
        :rtype: str
        """
        parts = PurePosixPath(name).parts
        safe_parts = [
            secure_filename(part) for part in parts if part not in ("..", ".", "")
        ]

        if not safe_parts:
            raise ValueError("Invalid object key")
        return str(PurePosixPath(*safe_parts))

    @override
    async def get_size(self, name: str) -> int:
        """
        Retrieve the size of an S3 object in bytes.

        :param name: The object key (path) in the S3 bucket.
        :type name: str
        :return: The file size in bytes, or ``0`` if the object does not exist.
        :rtype: int
        :raises botocore.exceptions.ClientError: If an unexpected S3 error occurs.
        """
        name = self.get_name(name)

        async with self._get_s3_client() as s3_client:
            try:
                res = await s3_client.head_object(Bucket=self.bucket_name, Key=name)
                return int(res.get("ContentLength", 0))
            except ClientError as e:
                code = e.response.get("Error", {}).get("Code")
                status = e.response.get("ResponseMetadata", {}).get("HTTPStatusCode")

                if code in ("NoSuchKey", "NotFound") or status == 404:
                    return 0
                raise

    @override
    async def get_path(self, name: str) -> str:
        """
        Generate a URL for accessing an S3 object.

        If ``custom_domain`` is set, returns a static URL using that domain.
        If ``querystring_auth`` is True, returns a presigned URL with temporary access.

        :param name: The object key (path) in the S3 bucket.
        :type name: str
        :return: A direct or presigned URL for the file.
        :rtype: str
        """
        if self.custom_domain:
            return f"{self._http_scheme}://{self.custom_domain}/{name}"
        elif self.querystring_auth:
            async with self._get_s3_client() as s3_client:
                params = {"Bucket": self.bucket_name, "Key": name}
                return await s3_client.generate_presigned_url(
                    "get_object", Params=params
                )
        else:
            url = f"{self._http_scheme}://{self.endpoint_url}/{self.bucket_name}/{name}"
            return url

    @override
    async def open(self, name: str) -> BytesIO:
        """
        Open an object from S3 and return it as an in-memory binary stream.

        This method fetches the file contents asynchronously and returns
        a ``BytesIO`` object positioned at the start of the file.

        :param name: The object key (path) in the S3 bucket.
        :type name: str
        :return: A BytesIO object containing the file's contents.
        :rtype: BytesIO
        :raises FileNotFoundError: If the object is not found.
        :raises botocore.exceptions.ClientError: If the object cannot be fetched.
        """
        name = self.get_name(name)

        async with self._get_s3_client() as s3_client:
            try:
                response = await s3_client.get_object(Bucket=self.bucket_name, Key=name)
            except ClientError as e:
                code = e.response.get("Error", {}).get("Code")
                if code in ("NoSuchKey", "NotFound"):
                    raise FileNotFoundError(
                        f"Object not found in bucket: {name}"
                    ) from e
                raise

            async with response["Body"] as stream:
                data = await stream.read()
        return BytesIO(data)

    @override
    async def upload(self, file: BinaryIO, name: str) -> str:
        """
        Upload a file object to the configured S3 bucket.

        :param file: Binary file-like object to upload.
        :type file: BinaryIO
        :param name: Target object key (path) in the S3 bucket.
        :type name: str
        :return: The name or key of the uploaded object.
        :rtype: str
        :raises botocore.exceptions.ClientError: If the upload fails.
        """
        name = self.get_name(name)
        content_type, _ = mimetypes.guess_type(name)
        extra_args = {"ContentType": content_type or "application/octet-stream"}
        if self.default_acl:
            extra_args["ACL"] = self.default_acl

        async with self._get_s3_client() as s3_client:
            file.seek(0)
            await s3_client.put_object(
                Bucket=self.bucket_name, Key=name, Body=file, **extra_args
            )
        return name

    @override
    async def delete(self, name: str) -> None:
        """
        Delete an object from the S3 bucket.

        :param name: The object key (path) to delete.
        :type name: str
        :return: None
        :rtype: None
        :raises botocore.exceptions.ClientError: If the delete operation fails.
        """
        async with self._get_s3_client() as s3_client:
            try:
                await s3_client.delete_object(Bucket=self.bucket_name, Key=name)
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") != "NoSuchKey":
                    raise
