# TODO: replace FROM
FROM tiencheng/inference-engine:1.0.0-py3.9-gr2.9.4-cuda11.8-cudnn8.6
RUN mkdir /app
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y gcc libc6-dev git libgl1
ADD https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt /app/yolov7.pt
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/app.py"]
