# TODO: replace FROM
FROM tiencheng/inference-engine:gradio-v2.9.4
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/app.py"]
