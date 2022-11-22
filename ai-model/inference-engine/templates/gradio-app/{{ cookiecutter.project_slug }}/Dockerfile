# TODO: replace FROM
FROM inference-engine:{{ cookiecutter.version }}
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/main.py"]
