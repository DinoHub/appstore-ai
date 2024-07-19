from typing import List
from config import config

inputs: List[str] = ["text", "slider"]
outputs: List[str] = ['text']

def predict(name, intensity) -> str:
    return "Hello " + name + "!" * int(intensity)