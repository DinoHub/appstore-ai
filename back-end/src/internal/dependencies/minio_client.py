"""Contains functions to connect to MinIO instance and upload data to it"""
from io import BytesIO
from typing import Optional
from aiohttp import client_reqrep

import miniopy_async
from miniopy_async.commonconfig import CopySource, ComposeSource
from miniopy_async.deleteobjects import DeleteObject
from colorama import Fore

from ...config.config import config
from ...models.common import S3Storage


async def minio_api_client() -> Optional[miniopy_async.Minio]:
    """Create a MinIO API Client.

    Returns:
        Optional[miniopy_async.Minio]: MinIO API Client. If connection fails, returns None.
    """
    try:
        print(
            f"{Fore.GREEN}INFO{Fore.WHITE}:\t  Attempting to connect to MinIO instance @ {config.MINIO_DSN}..."
        )
        minio_client = miniopy_async.Minio(
            config.MINIO_DSN,  # use internal DNS name
            config.MINIO_API_ACCESS_KEY,
            config.MINIO_API_SECRET_KEY,
            secure=config.MINIO_TLS,
        )  # connect to minio using provided variables
        print(f"{Fore.GREEN}INFO{Fore.WHITE}:\t  MinIO client connected!")
        bucket_name = config.MINIO_BUCKET_NAME
        found_bucket = await minio_client.bucket_exists(bucket_name)
        # create the bucket from env variables if not already created
        if not found_bucket:
            await minio_client.make_bucket(bucket_name)
            print(f"{Fore.GREEN}INFO{Fore.WHITE}:\t  Bucket '{bucket_name}' created")
        else:
            print(f"{Fore.GREEN}INFO{Fore.WHITE}:\t  Bucket '{bucket_name}' already exists")
        return minio_client
    except :
        print(f"{Fore.YELLOW}WARNING{Fore.WHITE}:  Failed to connect to MinIO instance")


async def get_presigned_url(client: miniopy_async.Minio, object_name: str, bucket_name: str) -> str:
    """Get presigned URL to object in S3 bucket

    Args:
        client (miniopy_async.Minio): S3 Client
        object_name (str): Name of object to get signedurl for
        bucket_name (str): Name of bucket where bucket is stored

    Returns:
        str: presigned url
    """
    url = await client.presigned_get_object(
        bucket_name=bucket_name,
        object_name=object_name,
    )
    url = url.removeprefix("https://")  # type: ignore #ignore
    url = url.removeprefix("http://")  # type: ignore #ignore
    url = url.replace(config.MINIO_DSN or "", config.MINIO_API_HOST or "")  # type: ignore #ignore
    return url  # type: ignore #ignore


async def remove_data(
    client: miniopy_async.Minio,
    object_name: str,
    bucket_name: str,
):
    """Removes data from MinIO bucket

    Args:
        client (minio.Minio): S3 client
        object_name (str): Name of object to remove
        bucket_name (str): Name of bucket to remove object from
    """
    # remove data from S3 bucket
    await client.remove_object(
        bucket_name=bucket_name,
        object_name=object_name,
    )


async def remove_data_from_prefix(
    client: miniopy_async.Minio,
    prefix: str,
    bucket_name: str,
):
    objects_list = await client.list_objects(bucket_name=bucket_name, prefix=prefix, recursive=True)
    delete_object_list = map(lambda x: DeleteObject(x.object_name), objects_list)  # type: ignore #ignore
    errors = await client.remove_objects(bucket_name, delete_object_list)
    return errors


async def upload_data(
    client: miniopy_async.Minio,
    blob: bytes,
    object_name: str,
    bucket_name: str,
    content_type: str = "application/octet-stream",
) -> str:
    """Stores blob in MinIO bucket and returns URL to object

    Args:
        client (miniopy_async.Minio): MinIO client
        blob (bytes): Binary data to store
        object_name (str): Filename of object
        bucket_name (str): Bucket to store object in
        content_type (str, optional): Content type of object. Defaults to "application/octet-stream".

    Returns:
        str: an S3 URL to the object (need to be further processed)
    """
    data_stream = BytesIO(blob)
    # read whole stream to get length
    content_length = len(data_stream.read())
    data_stream.seek(0)  # reset stream to beginning
    # upload data to MinIO
    await client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=data_stream,
        length=content_length,
        content_type=content_type,
    )

    # NOTE: if bucket policy is not set to download, then this URL will not work
    return f"s3://{bucket_name}/{object_name}"


async def get_data(
    client: miniopy_async.Minio,
    object_name: str,
    bucket_name: str,
) -> client_reqrep.ClientResponse:
    """Retreives object from desired bucket and returns data as a response

    Args:
        client (miniopy_async.Minio): MinIO client
        object_name (str): Filename of object
        bucket_name (str): Bucket object is stored in

    Returns:
        response (urllib3.response.HTTPResponse): Response object containing data of object retrieved from bucket
    """
    response = await client.get_object(
        bucket_name=bucket_name,
        object_name=object_name,
    )
    return response


async def copy_data(
    client: miniopy_async.Minio,
    source_object_name: str,
    source_bucket_name: str,
    target_object_name: str,
    target_bucket_name: str,
) -> str:
    """Copies object from source bucket to desired bucket

    Args:
        client (miniopy_async.Minio): MinIO client
        source_object_name (str): Original name of object
        source_bucket_name (str): Source bucket object is stored in
        target_object_name (str): Desired name of object
        target_bucket_name (str): Desired bucket to store copied object in

    Returns:
        str: an S3 URL to the object (need to be further processed)
    """
    await client.copy_object(
        target_bucket_name,
        target_object_name,
        CopySource(source_bucket_name, source_object_name),
    )
    return f"s3://{target_bucket_name}/{target_object_name}"


async def compose_data(
    client: miniopy_async.Minio,
    sources: list[S3Storage],
    target_object_name: str,
    target_bucket_name: str,
) -> str:
    """Create an object by combining data from different source objects using server-side copy

    Args:
        client (miniopy_async.Minio): MinIO client
        sources (list[S3Storage]): List of buckets and objects to copy in dictionary form with key values 'bucket_name' and 'object_name'
        target_object_name (str): Desired name of object
        target_bucket_name (str): Desired bucket to store copied object in

    Returns:
        str: an S3 URL to the object (need to be further processed)
    """
    copy_source = []
    for x in sources:
        copy_source.append(ComposeSource(x.bucket_name, x.object_name))
    await client.compose_object(target_bucket_name, target_object_name, copy_source)

    return f"s3://{target_bucket_name}/{target_object_name}"
