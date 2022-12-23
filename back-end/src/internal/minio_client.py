import minio
from ..config.config import config
from colorama import Fore


def minio_api_client():
    try:
        print(
            f"{Fore.GREEN}INFO{Fore.WHITE}:\t  Attempting to connect to MinIO instance @ {config.MINIO_DSN}..."
        )
        minio_client = minio.Minio(
            config.MINIO_DSN,
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
