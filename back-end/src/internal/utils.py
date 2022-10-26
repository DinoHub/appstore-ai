import re


def to_snake_case(string: str) -> str:
    return (
        re.sub(r"(?<=[a-z])(?=[A-Z])|[^a-zA-Z]", "_", re.escape(string))
        .strip("_")
        .lower()
    )
