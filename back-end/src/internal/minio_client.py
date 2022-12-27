from io import BytesIO
from typing import Optional

import minio
from colorama import Fore

from ..config.config import config


def minio_api_client() -> Optional[minio.Minio]:
    try:
        print(
            f"{Fore.GREEN}INFO{Fore.WHITE}:\t  Attempting to connect to MinIO instance @ {config.MINIO_API_HOST}..."
        )
        minio_client = minio.Minio(
            config.MINIO_API_HOST,
            config.MINIO_API_ACCESS_KEY,
            config.MINIO_API_SECRET_KEY,
            secure=config.MINIO_TLS,
        )
        print(f"{Fore.GREEN}INFO{Fore.WHITE}:\t  MinIO client connected!")
        bucket_name = config.MINIO_BUCKET_NAME
        found_bucket = minio_client.bucket_exists(bucket_name)
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


def upload_data(
    client: minio.Minio,
    blob: bytes,
    object_name: str,
    bucket_name: str,
    content_type: str = "application/octet-stream",
) -> str:
    """Stores blob in MinIO bucket and returns URL to object

    :param client: MinIO client
    :type client: minio.Minio
    :param blob: Binary data to store
    :type blob: bytes
    :param object_name: filename of object
    :type object_name: str
    :param bucket_name: name of bucket to store object in
    :type bucket_name: str
    :param content_type: Content type of object, defaults to "application/octet-stream"
    :type content_type: str, optional
    :return: A URL to the object
    :rtype: str
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
    return f"{config.MINIO_API_HOST}/{bucket_name}/{object_name}"
