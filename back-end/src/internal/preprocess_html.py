"""This module contains functions for preprocessing HTML before it is saved to the database."""
from base64 import b64decode
from mimetypes import guess_extension
from uuid import uuid4

from bs4 import BeautifulSoup
from lxml.etree import ParserError
from lxml.html.clean import Cleaner

from ..config.config import config
from .minio_client import minio_api_client, upload_data


def preprocess_html(html: str) -> str:
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
    soup = upload_b64_media(soup)

    # Sanitize HTML
    html = sanitize_html(str(soup))

    return html


def upload_b64_media(parser: BeautifulSoup) -> BeautifulSoup:
    """Uploads base64 encoded images to S3 Compliant Storage.

    Args:
        parser (BeautifulSoup): HTML parser

    Returns:
        BeautifulSoup: Parser with base64 encoded images replaced with data URIs
    """
    s3_client = minio_api_client()
    if not s3_client:
        return parser
    # Get all images
    images = parser.find_all("img")
    for image in images:
        # Filter out images that are not base64 encoded
        if not image["src"].startswith("data:image"):
            continue
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
        url = upload_data(
            s3_client,
            decoded_image,
            path,
            config.MINIO_BUCKET_NAME,
            image_type,
        )

        # Replace the base64 encoded image with the URL of the uploaded image
        image["src"] = url
    return parser


def sanitize_html(html: str) -> str:
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
        cleaned: str = cleaner.clean_html(html) # type: ignore
        if not isinstance(cleaned, str):
            raise TypeError
        return cleaned
    except (ParserError, TypeError):
        return "Error!"
