from inference_engine import InferenceEngine, MediaFileIO, TextIO
from process import predict

engine = InferenceEngine.from_yaml("config.yaml")
engine.entrypoint(predict, TextIO, MediaFileIO)

if __name__ == "__main__":
    engine.serve(workers=4, module_import_str="main:engine.engine")
