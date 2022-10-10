from inference_engine import TextIO


def predict(data: TextIO) -> TextIO:
    """User prediction function. Takes data structured using the
    TextIO interface and returns data structured using
    a TextIO interface.

    :param data: # TODO: Add description
    :type data: TextIO
    :return: # TODO: Add description
    :rtype: TextIO
    """
    text = data.text
    return TextIO(text=text)
