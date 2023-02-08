"""Contains functions to connect to MinIO instance and upload data to it"""
from io import BytesIO
from typing import Optional
import urllib3

import minio
from minio.commonconfig import CopySource, ComposeSource
from minio.deleteobjects import DeleteObject
from colorama import Fore

from ...config.config import config
from ...models.common import S3Storage


def minio_api_client() -> Optional[minio.Minio]:
    """Create a MinIO API Client.

    Returns:
        Optional[minio.Minio]: MinIO API Client. If connection fails, returns None.
    """
    try:
        print(
            f"{Fore.GREEN}INFO{Fore.WHITE}:\t  Attempting to connect to MinIO instance @ {config.MINIO_DSN}..."
        )
        minio_client = minio.Minio(
            config.MINIO_DSN,  # use internal DNS name
            config.MINIO_API_ACCESS_KEY,
            config.MINIO_API_SECRET_KEY,
            secure=config.MINIO_TLS,
        )  # connect to minio using provided variables
        print(f"{Fore.GREEN}INFO{Fore.WHITE}:\t  MinIO client connected!")
        bucket_name = config.MINIO_BUCKET_NAME
        found_bucket = minio_client.bucket_exists(bucket_name)
        # create the bucket from env variables if not already created
        if not found_bucket:
            minio_client.make_bucket(bucket_name)
            print(f"{Fore.GREEN}INFO{Fore.WHITE}:\t  Bucket '{bucket_name}' created")
        else:
            print(
                f"{Fore.GREEN}INFO{Fore.WHITE}:\t  Bucket '{bucket_name}' already exists"
            )
        return minio_client
    except:
        print(
            f"{Fore.YELLOW}WARNING{Fore.WHITE}:\t  Failed to connect to MinIO instance"
        )


def get_presigned_url(client: minio.Minio, object_name: str, bucket_name: str) -> str:
    """Get presigned URL to object in S3 bucket

    Args:
        client (minio.Minio): S3 Client
        object_name (str): Name of object to get signedurl for
        bucket_name (str): Name of bucket where bucket is stored

    Returns:
        str: presigned url
    """
    url = client.presigned_get_object(
        bucket_name=bucket_name,
        object_name=object_name,
    )
    url = url.removeprefix("https://")
    url = url.removeprefix("http://")
    url = url.replace(config.MINIO_DSN or "", config.MINIO_API_HOST or "")
    return url


def remove_data(
    client: minio.Minio,
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
    client.remove_object(
        bucket_name=bucket_name,
        object_name=object_name,
    )


def remove_data_from_prefix(
    client: minio.Minio,
    prefix: str,
    bucket_name: str,
):
    delete_object_list = map(
        lambda x: DeleteObject(x.object_name),
        client.list_objects(bucket_name=bucket_name, prefix=prefix, recursive=True),
    )
    errors = client.remove_objects(bucket_name, delete_object_list)
    return errors


def upload_data(
    client: minio.Minio,
    blob: bytes,
    object_name: str,
    bucket_name: str,
    content_type: str = "application/octet-stream",
) -> str:
    """Stores blob in MinIO bucket and returns URL to object

    Args:
        client (minio.Minio): MinIO client
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
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=data_stream,
        length=content_length,
        content_type=content_type,
    )

    # NOTE: if bucket policy is not set to download, then this URL will not work
    return f"s3://{bucket_name}/{object_name}"


def get_data(
    client: minio.Minio,
    object_name: str,
    bucket_name: str,
) -> urllib3.response.HTTPResponse:
    """Retreives object from desired bucket and returns data as a response

    Args:
        client (minio.Minio): MinIO client
        object_name (str): Filename of object
        bucket_name (str): Bucket object is stored in

    Returns:
        response (urllib3.response.HTTPResponse): Response object containing data of object retrieved from bucket
    """
    response = client.get_object(
        bucket_name=bucket_name,
        object_name=object_name,
    )
    return response


def copy_data(
    client: minio.Minio,
    source_object_name: str,
    source_bucket_name: str,
    target_object_name: str,
    target_bucket_name: str,
) -> str:
    """Copies object from source bucket to desired bucket

    Args:
        client (minio.Minio): MinIO client
        source_object_name (str): Original name of object
        source_bucket_name (str): Source bucket object is stored in
        target_object_name (str): Desired name of object
        target_bucket_name (str): Desired bucket to store copied object in

    Returns:
        str: an S3 URL to the object (need to be further processed)
    """
    client.copy_object(
        target_bucket_name,
        target_object_name,
        CopySource(source_bucket_name, source_object_name),
    )
    return f"s3://{target_bucket_name}/{target_object_name}"


def compose_data(
    client: minio.Minio,
    sources: list[S3Storage],
    target_object_name: str,
    target_bucket_name: str,
) -> str:
    """Create an object by combining data from different source objects using server-side copy

    Args:
        client (minio.Minio): MinIO client
        sources (list[S3Storage]): List of buckets and objects to copy in dictionary form with key values 'bucket_name' and 'object_name'
        target_object_name (str): Desired name of object
        target_bucket_name (str): Desired bucket to store copied object in

    Returns:
        str: an S3 URL to the object (need to be further processed)
    """
    copy_source = []
    for x in sources:
        copy_source.append(ComposeSource(x.bucket_name, x.object_name))
    client.compose_object(target_bucket_name, target_object_name, copy_source)

    return f"s3://{target_bucket_name}/{target_object_name}"
