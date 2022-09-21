import os

from engine import predict
from fastapi import FastAPI, File, UploadFile
from schema import InferenceOutput

app = FastAPI(
    title="YOLOv4 Inference Engine"
)

@app.get("/")
async def hello_world():
    return {"message": "Hello World"}

@app.post("/predict", response_model=InferenceOutput)
async def make_prediction(media: UploadFile = File()):
    return (await predict(media))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, port=int(os.environ["PORT"]), host="0.0.0.0"
    )
