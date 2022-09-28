from executor import hello_world
from inference_engine import InferenceEngine, TextIO

engine = InferenceEngine.from_yaml("meta.yml")
engine.entrypoint(hello_world, TextIO, TextIO)
engine.serve()
