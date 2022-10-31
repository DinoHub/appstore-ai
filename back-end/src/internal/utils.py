import re


def uncased_to_snake_case(string: str) -> str:
    return "_".join(string.lower().split(" "))


def camel_case_to_snake_case(string: str) -> str:
    string = re.sub(r"[\-\.\s]", "_", str(string))
    if not string:
        return string
    return (
        string[0]
        + re.sub(r"[A-Z]", lambda matched: "_" + matched.group(0), string[1:])
    ).lower()


def to_camel_case(string: str) -> str:
    string_split = string.split("_")
    return string_split[0] + "".join(
        word.capitalize() for word in string_split[1:]
    )
