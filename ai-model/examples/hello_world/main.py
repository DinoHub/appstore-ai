from inference_engine import InferenceEngine, TextIO
from process import predict

engine = InferenceEngine.from_yaml("config.yaml")

engine.entrypoint(predict, TextIO, TextIO)

if __name__ == "__main__":
    engine.serve()
