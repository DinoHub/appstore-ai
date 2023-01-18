from subprocess import run, CalledProcessError
from pathlib import Path
from shutil import copytree, rmtree

# Remove paths depending on options
REMOVE_PATHS = [
    '{% if cookiecutter.inference_backend != "Triton" %} src/triton_utils.py {% endif %}'
]

for path in REMOVE_PATHS:
    path = path.strip()
    if path == "":
        continue
    path = Path(path.strip())
    if path.exists():
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()

# Load in example
example_task = "{{ cookiecutter.example_task }}".strip()
# Try to find folders in /examples with same task name
task_folder = Path(f"examples/{example_task}")

if task_folder.exists():
    # If exists, copy over example script
    copytree(str(task_folder), ".", dirs_exist_ok=True)

# Remove examples folder
rmtree("examples", ignore_errors=True)

