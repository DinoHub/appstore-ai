from typing import Optional

from fastapi import FastAPI


class Executor:
    def __init__(self, name: Optional[str] = None):
        self.app = FastAPI()