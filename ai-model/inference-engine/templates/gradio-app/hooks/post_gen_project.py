from pathlib import Path

# Remove paths depending on options
REMOVE_PATHS = [
    '{% if cookiecutter.inference_backend != "Triton" %} src/triton_utils.py {% endif %}'
]

for path in REMOVE_PATHS:
    path = Path(path.strip())
    path.unlink(missing_ok=True)
