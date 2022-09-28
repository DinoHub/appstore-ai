from tempfile import NamedTemporaryFile

from fastapi import File, UploadFile

CHUNK_SIZE = 4096


def download_file(file: UploadFile = File()) -> str:
    with NamedTemporaryFile(delete=False) as f:
        filename = f.name
        while content := file.file.read(CHUNK_SIZE):
            f.write(content)
    return filename
