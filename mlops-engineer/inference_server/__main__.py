import onnxruntime as ort
import os
from typing import List
import numpy as np
import onnxruntime as ort

from fastapi import FastAPI, File, UploadFile, HTTPException,Query,Depends, Request

from inference_server.config import settings
from inference_server.models import Model
from inference_server.schemas import InferencePayload, InferenceResult

from pydantic import BaseModel

app = FastAPI()
models: dict[str, Model] = dict()

@app.get("/api/v1/list")
def list_models():
    return list(map(lambda x: x.stem, settings.models_dir.glob("*.onnx")))

@app.post("/api/v1/load")
def load_model(name: str):
    model_path = settings.models_dir / f"{name}.onnx"
    if not model_path.exists():
        raise HTTPException(
            status_code=404, detail=f"Model with name {name} not found."
        )
    if name not in models:
        models[name] = Model(model_path, autoload=True)
    return 200

@app.post("/api/v1/run/{name}")
def run_model(name: str, payload: InferencePayload):
    if name not in models:
        raise HTTPException(
            status_code=409, detail=f"No model with name {name} has been loaded."
        )
    result = models[name].from_bytes(payload.image)
    return InferenceResult(category=result)

@app.post("/api/v1/unload")
def unload_model(name: str):
    if name not in models:
        raise HTTPException(
            status_code=409, detail=f"No model with name {name} has been loaded."
        )
    del models[name]
    return 200



@app.post("/api/v1/register")
async def register_model(
    model_name: str = Query(..., description="The name of the model to register"),
    file: UploadFile = File(..., description="The ONNX model file")
):
    if not model_name or not file:
        raise HTTPException(status_code=400, detail="Model name and file are required")

    model_dir = "./models"
    file_path = os.path.join(model_dir, f"{model_name}.onnx")

    if os.path.exists(file_path):
        raise HTTPException(status_code=409, detail="A model with the same name already exists")

    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving model file: {str(e)}")

    # Update the list of available models
    # ...

    return {"message": "Model registered successfully"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
