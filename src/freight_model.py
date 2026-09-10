import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

FEATURES = ["Dollars", "Quantity", "VendorNumber", "days_po_to_invoice", "po_month", "po_day_of_week"]
TARGET = "Freight"

def build_model():
    numeric = ["Dollars", "Quantity", "days_po_to_invoice", "po_month", "po_day_of_week"]
    categorical = ["VendorNumber"]
    preprocessor = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), numeric),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    return Pipeline([("preprocessor", preprocessor), ("model", ExtraTreesRegressor(n_estimators=300, random_state=42, n_jobs=-1))])

def predict_freight(model, dollars, quantity, vendor_number, days_po_to_invoice=7, po_month=1, po_day_of_week=0):
    row = pd.DataFrame([{ "Dollars": dollars, "Quantity": quantity, "VendorNumber": vendor_number, "days_po_to_invoice": days_po_to_invoice, "po_month": po_month, "po_day_of_week": po_day_of_week }])
    return float(model.predict(row)[0])
