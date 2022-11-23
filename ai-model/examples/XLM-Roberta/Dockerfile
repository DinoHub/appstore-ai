# TODO: replace FROM
FROM tiencheng/inference-engine:latest
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/app.py"]
