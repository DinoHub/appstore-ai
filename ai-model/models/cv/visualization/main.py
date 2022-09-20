import os

from engine import visualize
from fastapi import FastAPI, File, UploadFile, Form

app = FastAPI()

@app.get("/")
async def hello_world():
    return {"message": "Hello World"}

@app.post("/visualize")
async def make_visualization(
    inputs: UploadFile = File(),
    outputs: str = Form(description="Stringified JSON output of model")
):
    return (await visualize(inputs, outputs))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, port=int(os.environ.get("PORT", 5002)), host="0.0.0.0"
    )
