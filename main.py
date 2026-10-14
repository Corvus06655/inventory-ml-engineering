"""FastAPI service for the Inventory & Vendor Intelligence project.

The API uses inventory.db when a compatible vendor_invoice table is present.
If the database is absent, it falls back to deterministic synthetic demo data.
Demo predictions are for demonstrating the API only, not real procurement decisions.
"""
from pathlib import Path
import sqlite3
from typing import Literal

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AliasChoices, BaseModel, Field
from sklearn.ensemble import RandomForestRegressor

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "inventory.db"

app = FastAPI(
    title="Inventory & Vendor Intelligence API",
    description=(
        "Freight-cost estimation and rule-based invoice screening. "
        "When inventory.db is unavailable, the freight model uses synthetic demo data."
    ),
    version="1.0.0",
)

# Permit the deployed portfolio frontend to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    # Public demo API: allow browser requests from the deployed portfolio frontend.
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

model: RandomForestRegressor | None = None
data_mode: Literal["database", "demo"] = "demo"
training_rows = 0


def _demo_data() -> pd.DataFrame:
    """Build reproducible synthetic data for safe, database-free API demos."""
    rng = np.random.default_rng(42)
    dollars = rng.uniform(500, 30_000, 800)
    quantity = rng.integers(1, 500, 800)
    freight = np.maximum(5, 0.011 * dollars + 0.015 * quantity + rng.normal(0, 35, 800))
    return pd.DataFrame({"Dollars": dollars, "Freight": freight})


def _load_training_data() -> tuple[pd.DataFrame, str]:
    if DB_PATH.exists():
        try:
            with sqlite3.connect(DB_PATH) as conn:
                tables = pd.read_sql_query(
                    "SELECT name FROM sqlite_master WHERE type='table'", conn
                )["name"].tolist()
                if "vendor_invoice" in tables:
                    df = pd.read_sql_query(
                        "SELECT Dollars, Freight FROM vendor_invoice", conn
                    )
                    df = df.replace([np.inf, -np.inf], np.nan).dropna()
                    df = df[(df["Dollars"] >= 0) & (df["Freight"] >= 0)]
                    if len(df) >= 10:
                        return df, "database"
        except (sqlite3.Error, pd.errors.DatabaseError):
            pass
    return _demo_data(), "demo"


@app.on_event("startup")
def train_freight_model() -> None:
    """Train a lightweight demonstration model from the available data source."""
    global model, data_mode, training_rows
    df, data_mode = _load_training_data()
    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=8)
    model.fit(df[["Dollars"]], df["Freight"])
    training_rows = len(df)


class FreightPredictionRequest(BaseModel):
    invoice_dollars: float = Field(ge=0, le=1_000_000_000, description="Invoice value in dollars")


class FreightPredictionResponse(BaseModel):
    predicted_freight: float
    currency: str = "same unit as training data"
    data_mode: Literal["database", "demo"]
    training_rows: int
    note: str


class InvoiceCheckRequest(BaseModel):
    invoice_dollars: float = Field(
        ge=0, le=1_000_000_000,
        validation_alias=AliasChoices("invoice_dollars", "actual_total"),
    )
    purchase_total_dollars: float = Field(
        ge=0, le=1_000_000_000,
        validation_alias=AliasChoices("purchase_total_dollars", "expected_total"),
    )
    average_receiving_delay_days: float = Field(ge=0, le=36500)


@app.get("/", tags=["Health"])
def root() -> dict:
    return {
        "message": "Inventory & Vendor Intelligence API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health() -> dict:
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "data_mode": data_mode,
        "training_rows": training_rows,
    }


@app.post("/predict-freight", response_model=FreightPredictionResponse, tags=["Freight"])
def predict_freight(payload: FreightPredictionRequest) -> FreightPredictionResponse:
    if model is None:
        raise HTTPException(status_code=503, detail="Freight model is not ready")
    prediction = float(model.predict(pd.DataFrame({"Dollars": [payload.invoice_dollars]}))[0])
    note = (
        "Uses local inventory.db data. Validate model quality before operational use."
        if data_mode == "database"
        else "DEMO ONLY: trained on synthetic data; do not use for real purchasing decisions."
    )
    return FreightPredictionResponse(
        predicted_freight=round(max(0.0, prediction), 2),
        data_mode=data_mode,
        training_rows=training_rows,
        note=note,
    )


@app.post("/validate-invoice", tags=["Invoice Screening"])
def validate_invoice(payload: InvoiceCheckRequest) -> dict:
    mismatch = abs(payload.invoice_dollars - payload.purchase_total_dollars)
    mismatch_flag = mismatch > 5
    delay_flag = payload.average_receiving_delay_days > 10
    reasons = []
    if mismatch_flag:
        reasons.append("Invoice and purchase totals differ by more than $5.")
    if delay_flag:
        reasons.append("Average receiving delay exceeds 10 days.")
    if not reasons:
        reasons.append("No configured rule was triggered.")

    return {
        "status": "FLAGGED" if mismatch_flag or delay_flag else "NORMAL",
        "flagged": mismatch_flag or delay_flag,
        "dollar_mismatch": round(mismatch, 2),
        "thresholds": {
            "dollar_mismatch_gt": 5,
            "average_receiving_delay_days_gt": 10,
        },
        "reasons": reasons,
        "disclaimer": (
            "Rule-based screening signal only; a flag is not proof of fraud or misconduct."
        ),
    }
