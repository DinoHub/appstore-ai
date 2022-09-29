from executor import predict
from inference_engine import (
    InferenceEngine,
    SingleMediaFileIO,
    TextIO,
    media_type,
)

engine = InferenceEngine.from_yaml("meta.yaml")
engine.entrypoint(
    predict, TextIO, SingleMediaFileIO, media_type=media_type.jpeg
)

if __name__ == "__main__":
    engine.serve()
