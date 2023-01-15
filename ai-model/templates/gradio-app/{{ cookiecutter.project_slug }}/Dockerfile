# TODO: replace FROM
FROM tiencheng/inference-engine:1.0.0-py{{ cookiecutter.python_version }}-gr{{ cookiecutter.gradio_version }}-{{ cookiecutter.hardware }}
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/app.py"]
