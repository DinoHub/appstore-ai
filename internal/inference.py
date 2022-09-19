# import tritonclient.http as httpclient

# from config.config import config

# triton_client = httpclient.InferenceServerClient(url=config.TRITON_URL)


# def is_triton_inference(url: str) -> bool:
#     """
#     This is just a tmp function to simulate the logic of
#     figuring out which inference engine to use.
#     Possible ways to tell
#     1. User states somewhere in model card metadata
#     2. Distinct clue from the inference URL provided
#     Easiest way is if its just set by user.
#     """
#     return True  # See docstring
