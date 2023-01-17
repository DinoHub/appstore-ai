FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ARG PORT=5002
ENV PORT=${PORT}
EXPOSE ${PORT}
CMD python main.py
