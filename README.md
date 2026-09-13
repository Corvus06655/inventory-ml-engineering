# Inventory & Vendor Intelligence with Predictive ML

A practical analytics and machine-learning project for vendor purchases, invoice transactions, freight costs, and invoice anomaly detection.

The project demonstrates a reproducible workflow from **SQLite data → SQL/Python feature engineering → exploratory analysis → ML modeling → saved artifacts**.

## What this project does

### 1. Freight Cost Prediction

Predicts invoice freight cost using:
- invoice dollars
- quantity
- vendor number
- PO-to-invoice delay
- PO month
- PO day of week

**Model:** ExtraTrees Regressor  
**Evaluation:** chronological 80/20 holdout  
**Metrics:** MAE, RMSE, R²

Current recorded holdout results:
- **R²: 0.9840**
- **MAE: 44.22**
- **RMSE: 108.74**

The chronological split keeps the latest observations for testing, making the evaluation more representative of predicting future transactions.

### 2. Invoice Anomaly Detection

Uses **Isolation Forest** to identify unusual vendor-invoice transactions based on transaction value, quantity, freight, timing, and related features.

This is deliberately treated as **unsupervised anomaly detection**, not fraud classification. A rule-derived invoice flag is not used as independent ML ground truth, avoiding a misleading supervised-learning claim.

## Project structure

```text
inventory-ml-engineering/
├── notebooks/
│   ├── freight_cost_prediction.ipynb
│   ├── invoice_anomaly_analysis.ipynb
│   └── README.md
├── src/
│   ├── data.py
│   ├── freight_model.py
│   └── invoice_anomaly.py
├── scripts/
│   ├── train_freight.py
│   └── run_anomaly_detection.py
├── app/
├── tests/
├── artifacts/
├── data/
├── DATA_DICTIONARY.md
├── requirements.txt
├── requirements-api.txt
├── Dockerfile
└── docker-compose.yml
```

## Dataset

The source SQLite database contains purchase, pricing, vendor-invoice, and inventory tables. The database is intentionally **not committed to GitHub** because of its size.

Place the database at the project root:

```text
data.db
```

## Reproduce the ML workflow

```bash
pip install -r requirements.txt
python scripts/train_freight.py
python scripts/run_anomaly_detection.py
```

The scripts create model outputs under `artifacts/`.

## Notebooks

The repository contains two focused notebooks:

- **freight_cost_prediction.ipynb** — EDA, chronological holdout, freight-cost modeling, evaluation, and interpretation.
- **invoice_anomaly_analysis.ipynb** — invoice feature exploration and Isolation Forest anomaly detection.

The notebooks are intentionally aligned with the reusable implementation in `src/` and `scripts/`.

## Engineering implementation

The ML code is separated from exploratory notebooks:

- `src/data.py` centralizes SQLite table loading.
- `src/freight_model.py` defines preprocessing and the ExtraTrees regression pipeline.
- `src/invoice_anomaly.py` defines the Isolation Forest detector.
- `scripts/` provides reproducible training/scoring entry points.
- `artifacts/` stores generated model outputs and evaluation summaries.

## Resume-ready project summary

**Inventory & Vendor Intelligence with Predictive ML | Python, SQL, Pandas, scikit-learn**

- Investigated vendor freight-cost drivers and invoice irregularities across purchase and invoice data using SQL and Python.
- Engineered PO-level and invoice-timing features for predictive modeling.
- Built an ExtraTrees freight-cost regression model achieving **R² = 0.984** on a chronological 80/20 holdout (MAE 44.22, RMSE 108.74).
- Applied Isolation Forest to identify anomalous invoice transactions without treating a rule-generated label as independent fraud ground truth.
