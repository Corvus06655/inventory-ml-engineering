from pathlib import Path
import json
import joblib
import pandas as pd
from src.data import load_table
from src.invoice_anomaly import build_detector, FEATURES

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)
df = load_table("vendor_invoice").copy()
for c in ["PODate", "InvoiceDate"]:
    df[c] = pd.to_datetime(df[c], errors="coerce")
df["days_po_to_invoice"] = (df["InvoiceDate"] - df["PODate"]).dt.days
df["days_to_pay"] = 0
df["total_brands"] = 1
df["total_quantity"] = df["Quantity"]
df["total_dollars"] = df["Dollars"]
df["avg_receiving_delay"] = 0
df = df.dropna(subset=["Dollars", "Quantity", "Freight"])
model = build_detector()
model.fit(df[FEATURES])
df["is_anomaly"] = model.predict(df[FEATURES]) == -1
df["anomaly_score"] = -model.decision_function(df[FEATURES])
df.sort_values("anomaly_score", ascending=False).to_csv(ARTIFACTS / "invoice_anomalies.csv", index=False)
joblib.dump(model, ARTIFACTS / "invoice_anomaly_detector.joblib")
summary = {"rows_scored": int(len(df)), "anomalies": int(df["is_anomaly"].sum()), "contamination": 0.05}
(ARTIFACTS / "anomaly_summary.json").write_text(json.dumps(summary, indent=2))
print(summary)
