class MaxFileSizeException(Exception):
    def __init__(self, fs: str):
        self.fs = fs

class MaxFileSizeValidator:
    def __init__(self, max_size: int):
        self.fs = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.fs += len(chunk)
        if self.fs > self.max_size:
            raise MaxFileSizeException(fs=self.fs)