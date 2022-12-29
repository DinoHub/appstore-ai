# TODO: replace FROM
FROM tiencheng/inference-engine:{{ cookiecutter.version }}
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/app.py"]
