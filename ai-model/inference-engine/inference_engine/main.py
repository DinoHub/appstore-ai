if __name__ == "__main__":
    # Note that this is purely for development purposes
    from core.engine import InferenceEngine

    engine = InferenceEngine()
    engine.serve()
