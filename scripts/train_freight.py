from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.data import load_table
from src.freight_model import build_model, FEATURES, TARGET

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)

df = load_table("vendor_invoice")
df["PODate"] = pd.to_datetime(df["PODate"], errors="coerce")
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
df["days_po_to_invoice"] = (df["InvoiceDate"] - df["PODate"]).dt.days
df["po_month"] = df["PODate"].dt.month
df["po_day_of_week"] = df["PODate"].dt.dayofweek
df = df.dropna(subset=[TARGET]).sort_values("PODate")
cut = int(len(df) * 0.8)
train, test = df.iloc[:cut], df.iloc[cut:]
model = build_model()
model.fit(train[FEATURES], train[TARGET])
pred = model.predict(test[FEATURES])
metrics = {"mae": float(mean_absolute_error(test[TARGET], pred)), "rmse": float(mean_squared_error(test[TARGET], pred) ** 0.5), "r2": float(r2_score(test[TARGET], pred)), "split": "chronological_80_20"}
joblib.dump(model, ARTIFACTS / "freight_model.joblib")
(ARTIFACTS / "freight_metrics.json").write_text(json.dumps(metrics, indent=2))
print(metrics)
