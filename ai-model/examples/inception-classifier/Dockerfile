FROM tiencheng/inference-engine:1.0.0-py3.9-gr3.16.1-cpu
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/app.py"]
