# Inventory ML Engineering Project

End-to-end ML engineering project for freight-cost prediction and vendor-invoice anomaly detection.

## ML problems

### Freight Cost Prediction — supervised regression
- SQL/Pandas feature engineering from PO and invoice dates
- Numeric imputation and vendor one-hot encoding
- ExtraTrees regression
- Chronological 80/20 evaluation to simulate future prediction
- MAE, RMSE and R² evaluation

Latest local chronological holdout: **R² 0.9840, MAE 44.22, RMSE 108.74**.

### Invoice Anomaly Detection — unsupervised learning
Uses purchase/invoice features, robust scaling and Isolation Forest to rank unusual invoices without using a hand-written rule as a fake ML ground truth.

## Important modeling decision

The original classifier used a `flagged_invoice` target created from business rules and then trained on the same variables. That is target leakage/circular labeling, so this version does not present that as a learned fraud classifier.

## Dataset

The original SQLite database contains purchase, pricing, vendor-invoice and inventory tables. `data.db` is intentionally excluded from GitHub because it is a large local dataset. Place it at the project root before training.

## Run

```bash
pip install -r requirements.txt
python scripts/train_freight.py
python scripts/run_anomaly_detection.py
```

## API

FastAPI endpoints:
- `GET /health`
- `POST /predict/freight`
- `POST /predict/anomaly`
- `GET /monitoring`
- `GET /docs`

Run after generating model artifacts:

```bash
uvicorn app.main:app --reload
```

## Docker

Generate `artifacts/*.joblib` locally first, then:

```bash
docker build -t inventory-ml-api .
docker run --rm -p 8000:8000 inventory-ml-api
```

## Testing

```bash
pytest -q
```

## Resume positioning

**Inventory & Vendor Invoice ML Pipeline | Python, SQL, scikit-learn**

- Built an end-to-end freight-cost regression pipeline using SQL/Pandas feature engineering, one-hot encoding and ExtraTrees; evaluated with MAE, RMSE and R² and persisted the trained model with Joblib.
- Developed an unsupervised invoice anomaly-detection workflow using purchase-order aggregates, robust scaling and Isolation Forest to rank unusual vendor invoices without target leakage.
- Refactored exploratory ML workflows into reusable Python modules and reproducible scripts, with FastAPI serving, Docker configuration and basic monitoring/testing.

Large local/generated files (`data.db`, trained `.joblib` files and scored CSV output) are excluded from Git history. The repository contains the reproducible source, notebooks, API, Docker configuration and evaluation metadata.
