import re


def uncased_to_snake_case(string: str) -> str:
    return "_".join(string.lower().split(" "))


def k8s_safe_name(string: str) -> str:
    """K8S names can only contain alphanum
    chars and hyphens, be lower case and
    names cannot start with hyphens.

    :param string: _description_
    :type string: str
    :return: _description_
    :rtype: str
    """
    return re.sub(r"[^a-z0-9\-]", "", string.lower().strip()).removeprefix("-")


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
