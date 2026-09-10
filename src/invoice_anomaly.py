import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline

FEATURES = ["Dollars", "Quantity", "Freight", "days_po_to_invoice", "days_to_pay", "total_brands", "total_quantity", "total_dollars", "avg_receiving_delay"]

def build_detector():
    return Pipeline([
        ("scaler", RobustScaler()),
        ("model", IsolationForest(n_estimators=300, contamination=0.05, random_state=42, n_jobs=-1)),
    ])
