from pathlib import Path

# Remove paths depending on options
REMOVE_PATHS = [
    '{% if cookiecutter.inference_backend != "Triton" %} src/triton_utils.py {% endif %}'
]

for path in REMOVE_PATHS:
    path = path.strip()
    if path == '':
        continue
    path = Path(path.strip())
    if path.exists():
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()
