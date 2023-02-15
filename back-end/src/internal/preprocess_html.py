"""This module contains functions for preprocessing HTML before it is saved to the database."""
from base64 import b64decode, b64encode
from mimetypes import guess_extension, guess_type
from uuid import uuid4

from bs4 import BeautifulSoup
from lxml.etree import ParserError
from lxml.html.clean import Cleaner

from ..config.config import config
from .dependencies.minio_client import (
    get_data,
    get_presigned_url,
    minio_api_client,
    upload_data,
)


async def preprocess_html_post(html: str) -> str:
    """Preprocessing pipeline for HTML.

    This function performs the following steps:
    1. Convert base64 encoded images to data URIs (upload to S3 Compliant Storage)
    2. Sanitize HTML

    Args:
        html (str): Raw HTML

    Returns:
        str: Preprocessed HTML
    """
    # Convert base64 encoded images to data URIs
    soup = BeautifulSoup(html, "lxml")
    soup = await upload_b64_media(soup)

    # Sanitize HTML
    html = await sanitize_html(str(soup))

    return html


async def preprocess_html_get(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    soup = await s3_url_to_presigned_url(soup)
    html = str(soup)
    return html


async def upload_b64_media(parser: BeautifulSoup) -> BeautifulSoup:
    """Uploads base64 encoded images to S3 Compliant Storage.

    Args:
        parser (BeautifulSoup): HTML parser

    Returns:
        BeautifulSoup: Parser with base64 encoded images replaced with data URIs
    """
    s3_client = await minio_api_client()
    if not s3_client:
        return parser
    # Get all images
    images = parser.find_all("img")
    for image in images:
        # Filter out images that are not base64 encoded
        if image["src"].startswith("data:image"):
            # Extract the base64 encoded image
            # e.g data:image/jpeg;base64,<BASE64 ENCODED IMAGE>
            b64_image = image["src"].split(",")
            # Get the image type
            image_type = b64_image[0].split(":")[1].split(";")[0]
            # Get the base64 encoded image
            b64_image = b64_image[1]
            # Decode the base64 encoded image
            decoded_image = b64decode(b64_image)

            # Generate a unique name for the image
            # note guess_extension returns a dot before the extension
            path = f"images/{uuid4()}{guess_extension(image_type)}"

            # Upload the image to S3
            # TODO: Allow customization of upload method
            url = await upload_data(
                s3_client,
                decoded_image,
                path,
                config.MINIO_BUCKET_NAME,
                image_type,
            )

            # Replace the base64 encoded image with the URL of the uploaded image
            image["src"] = url
        elif image["src"].startswith(config.MINIO_API_HOST):
            # When editing markdown, image retrieved will be a presignedurl, which needs to be converted back
            url = image["src"].removeprefix(config.MINIO_API_HOST).strip("/")
            bucket, path = url.split("/", 1)
            path = path.split("?", 1)[0]
            url = f"s3://{bucket}/{path}"
            image["src"] = url
    return parser


async def sanitize_html(html: str) -> str:
    """Sanitize HTML.

    Args:
        html (str): Input HTML

    Raises:
        TypeError: If the output of the cleaner is not a string

    Returns:
        str: Sanitized HTML
    """
    cleaner = Cleaner(
        comments=True,
        meta=True,
        page_structure=True,
        processing_instructions=True,
        forms=True,
        add_nofollow=True,
        whitelist_tags=["chart", "embed", "iframe"],
        safe_attrs_only=False,
        remove_unknown_tags=False,
    )
    try:
        cleaned: str = cleaner.clean_html(html)  # type: ignore
        if not isinstance(cleaned, str):
            raise TypeError
        return cleaned
    except (ParserError, TypeError) as err:
        print("Error sanitizing HTML", err)
        return "<p>Error parsing HTML</p>"


async def s3_url_to_presigned_url(
    parser: BeautifulSoup,
):
    s3_client = await minio_api_client()
    if not s3_client:
        return parser
    # Get all images
    images = parser.find_all("img")
    for image in images:
        # Filter out images that are not base64 encoded
        if not image["src"].startswith("s3://"):
            continue
        # Extract bucket name and object name
        # s3://<bucket>/<object>
        bucket_name, object_name = image["src"].split("s3://")[1].split("/", 1)

        # Replace the base64 encoded image with the URL of the uploaded image
        image["src"] = await get_presigned_url(s3_client, object_name, bucket_name)
    return parser


async def process_html_to_base64(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    soup = await s3_url_to_base64(soup)
    html = await sanitize_html(str(soup))
    return html


async def s3_url_to_base64(
    parser: BeautifulSoup,
):
    s3_client = await minio_api_client()
    if not s3_client:
        return parser
    # Get all images
    images = parser.find_all("img")
    for image in images:
        # Filter out images that are not base64 encoded
        if not image["src"].startswith("s3://"):
            continue
        # Extract bucket name and object name
        # s3://<bucket>/<object>
        bucket_name, object_name = image["src"].split("s3://")[1].split("/", 1)
        bytes_image = await get_data(s3_client, object_name, bucket_name)
        base64_image = b64encode(await bytes_image.read()).decode("utf-8")
        data_type = guess_type(object_name)[0]
        image["src"] = f"data:{data_type};base64,{base64_image}"
    return parser
