from executor import predict
from inference_engine import InferenceEngine, SingleMediaFileIO, TextIO

engine = InferenceEngine.from_yaml("meta.yaml")
engine.entrypoint(predict, TextIO, SingleMediaFileIO)

if __name__ == "__main__":
    engine.serve()
