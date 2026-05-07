from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .model_service import MODEL_PATH, ModelService
from .schemas import JobPostingInput, PredictionResponse


app = FastAPI(title="JobShield AI API", version="1.0.0")
service = ModelService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {"message": "JobShield AI API running"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": service.model is not None, "model_path": str(MODEL_PATH)}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: JobPostingInput) -> dict:
    try:
        return service.predict(payload)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc


@app.post("/train")
def train() -> dict:
    project_root = Path(__file__).resolve().parent.parent.parent
    dataset = project_root / "fake_job_postings.csv"
    train_script = project_root / "backend" / "train_model.py"

    if not dataset.exists():
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset}")

    cmd = [
        sys.executable,
        str(train_script),
        "--data",
        str(dataset),
        "--output",
        str(MODEL_PATH),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise HTTPException(status_code=500, detail=proc.stderr.strip() or proc.stdout.strip())
    service.load()
    return {"message": "Model trained and loaded", "logs": proc.stdout.strip()}
