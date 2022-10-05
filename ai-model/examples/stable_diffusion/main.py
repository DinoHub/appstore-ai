from inference_engine import InferenceEngine, MediaFileIO, TextIO, media_type
from process import predict

engine = InferenceEngine.from_yaml("config.yaml")
engine.entrypoint(predict, TextIO, MediaFileIO, media_type=media_type.jpeg)

if __name__ == "__main__":
    engine.serve()
