from inference_engine import InferenceEngine, SingleMediaFileIO, TextIO
from process import predict

engine = InferenceEngine.from_yaml("meta.yaml")
engine.entrypoint(predict, SingleMediaFileIO, TextIO, media_type=None)
if __name__ == "__main__":
    engine.serve()
