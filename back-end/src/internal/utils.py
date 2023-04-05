"""This module contains utility functions that are used throughout the project."""
import re


def uncased_to_snake_case(string: str) -> str:
    """Converts a string to snake case.

    Args:
        string (str): Input string

    Returns:
        str: Snake case string
    """
    return "_".join(string.lower().strip().split(" "))


def sanitize_for_url(string: str) -> str:
    url = ";,/?:@&=+$-_.!~*'()"
    remove_unsafe_chars = str.maketrans(url, "_" * len(url))
    return string.translate(remove_unsafe_chars)


def k8s_safe_name(string: str) -> str:
    """Converts a string to a k8s safe name.

    A k8s safe name can only contain alphanum
    chars and hyphens, be lower case and
    names cannot start with hyphens.
    Should also be <63 characters long

    Args:
        string (str): Input string

    Returns:
        str: Output string
    """
    # Give some leeway to allow for adding suffixes (e.g -deployment)
    return re.sub(r"[^a-z0-9\-]", "", string.lower().strip()).removeprefix(
        "-"
    )[:62]


def camel_case_to_snake_case(string: str) -> str:
    """Converts a string from camel case to snake case.

    Args:
        string (str): Camel case string

    Returns:
        str: Snake case string
    """
    string = re.sub(r"[\-\.\s]", "_", str(string).strip())
    if not string:
        return string
    return (
        string[0]
        + re.sub(r"[A-Z]", lambda matched: "_" + matched.group(0), string[1:])
    ).lower()


def to_camel_case(string: str) -> str:
    """Converts a string to camel case.

    Args:
        string (str): Input string

    Returns:
        str: Camel case string
    """
    string_split = string.split("_")
    return (
        string_split[0]
        + "".join(word.capitalize() for word in string_split[1:])
    ).strip()
