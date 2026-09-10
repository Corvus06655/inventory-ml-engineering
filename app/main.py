from pathlib import Path
import logging
import time
from threading import Lock
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("inventory-ml-api")
freight_model = None
anomaly_model = None
metrics = {"freight_predictions": 0, "anomaly_predictions": 0, "errors": 0, "total_latency_ms": 0.0}
metrics_lock = Lock()

class FreightRequest(BaseModel):
    dollars: float = Field(gt=0)
    quantity: float = Field(gt=0)
    vendor_number: int = Field(gt=0)
    days_po_to_invoice: float = Field(default=7, ge=0)
    po_month: int = Field(default=1, ge=1, le=12)
    po_day_of_week: int = Field(default=0, ge=0, le=6)

class AnomalyRequest(BaseModel):
    dollars: float = Field(gt=0)
    quantity: float = Field(gt=0)
    freight: float = Field(ge=0)
    days_po_to_invoice: float = Field(default=7, ge=0)
    days_to_pay: float = Field(default=0, ge=0)
    total_brands: float = Field(default=1, ge=0)
    total_quantity: float = Field(default=0, ge=0)
    total_dollars: float = Field(default=0, ge=0)
    avg_receiving_delay: float = Field(default=0, ge=0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global freight_model, anomaly_model
    try:
        freight_model = joblib.load(ARTIFACTS / "freight_model.joblib")
        anomaly_model = joblib.load(ARTIFACTS / "invoice_anomaly_detector.joblib")
        logger.info("ML models loaded successfully")
        yield
    except Exception:
        logger.exception("Failed to load model artifacts")
        raise
    finally:
        freight_model = None
        anomaly_model = None

app = FastAPI(title="Inventory ML API", description="Production-style API for freight-cost prediction and invoice anomaly scoring.", version="1.1.0", lifespan=lifespan)

def record(name: str, elapsed_ms: float):
    with metrics_lock:
        metrics[name] += 1
        metrics["total_latency_ms"] += elapsed_ms

@app.get("/", tags=["system"])
def root():
    return {"service": "inventory-ml-api", "status": "running", "docs": "/docs"}

@app.get("/health", tags=["system"])
def health():
    ready = freight_model is not None and anomaly_model is not None
    return {"status": "ok" if ready else "degraded", "models_loaded": ready}

@app.get("/monitoring", tags=["monitoring"])
def monitoring():
    with metrics_lock:
        prediction_count = metrics["freight_predictions"] + metrics["anomaly_predictions"]
        avg_latency = metrics["total_latency_ms"] / prediction_count if prediction_count else 0
        return {**metrics, "avg_prediction_latency_ms": round(avg_latency, 3)}

@app.post("/predict/freight", tags=["prediction"])
def predict_freight(request: FreightRequest):
    if freight_model is None:
        raise HTTPException(status_code=503, detail="Freight model is not loaded")
    started = time.perf_counter()
    try:
        row = pd.DataFrame([{"Dollars": request.dollars, "Quantity": request.quantity, "VendorNumber": request.vendor_number, "days_po_to_invoice": request.days_po_to_invoice, "po_month": request.po_month, "po_day_of_week": request.po_day_of_week}])
        prediction = float(freight_model.predict(row)[0])
        elapsed = (time.perf_counter() - started) * 1000
        record("freight_predictions", elapsed)
        logger.info("freight prediction vendor=%s latency_ms=%.2f", request.vendor_number, elapsed)
        return {"predicted_freight": round(max(0.0, prediction), 2), "unit": "dataset currency"}
    except Exception as exc:
        with metrics_lock: metrics["errors"] += 1
        logger.exception("Freight prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed") from exc

@app.post("/predict/anomaly", tags=["anomaly"])
def predict_anomaly(request: AnomalyRequest):
    if anomaly_model is None:
        raise HTTPException(status_code=503, detail="Anomaly model is not loaded")
    started = time.perf_counter()
    try:
        row = pd.DataFrame([request.model_dump()]).rename(columns={"dollars": "Dollars", "quantity": "Quantity", "freight": "Freight"})
        label = int(anomaly_model.predict(row)[0])
        score = float(-anomaly_model.decision_function(row)[0])
        elapsed = (time.perf_counter() - started) * 1000
        record("anomaly_predictions", elapsed)
        logger.info("anomaly prediction label=%s latency_ms=%.2f", label, elapsed)
        return {"is_anomaly": label == -1, "anomaly_score": round(score, 6)}
    except Exception as exc:
        with metrics_lock: metrics["errors"] += 1
        logger.exception("Anomaly scoring failed")
        raise HTTPException(status_code=500, detail="Anomaly scoring failed") from exc
