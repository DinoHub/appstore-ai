from inference_engine import TextIO


def hello_world(inputs: TextIO) -> TextIO:
    text = inputs.text

    text += "!!! Hello world!"

    return TextIO(text=text)
