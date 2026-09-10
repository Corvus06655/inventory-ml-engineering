# Inventory & Vendor Purchase Analytics + ML

An analytics-focused project for understanding vendor purchases, invoice behavior and freight costs using **SQL, Python, Pandas and scikit-learn**.

The project combines practical **data cleaning, SQL analysis, EDA, feature engineering and machine learning** on a large inventory / vendor-invoice dataset.

## What this project does

### 1. Vendor & Purchase Analytics

The notebooks use SQL and Python to explore:
- purchase and invoice records
- PO-level purchase aggregates
- invoice amounts and quantities
- freight costs
- PO-to-invoice and invoice-to-payment delays
- receiving delays and vendor-level patterns
- unusual invoice behavior

The analysis is designed to move from **raw transactional data → cleaned dataset → business observations → ML features**.

### 2. Freight Cost Prediction

A supervised regression model predicts freight cost using:
- invoice dollars
- quantity
- vendor number
- PO-to-invoice delay
- PO month
- PO day of week

**Model:** ExtraTrees Regressor  
**Evaluation:** chronological 80/20 holdout  
**Metrics:** MAE, RMSE and R²

Latest local chronological holdout:
- **R²: 0.9840**
- **MAE: 44.22**
- **RMSE: 108.74**

A chronological split is used because it is more representative of predicting future records than relying only on a random split.

### 3. Invoice Anomaly Analysis

The project also uses **Isolation Forest** to identify unusual invoice records based on transaction and timing characteristics.

This is intentionally treated as **anomaly detection**, not as supervised fraud classification, because the original `flagged_invoice` label was created from business rules. Training a classifier on the same rule-derived variables would create target leakage and give a misleading ML result.

## Project structure

```text
inventory-ml-engineering/
├── notebooks/
│   ├── Freight Prediction.ipynb
│   ├── invoice flagging.ipynb
│   └── Inventory_ML_End_to_End.ipynb
├── src/
│   ├── data.py
│   ├── freight_model.py
│   └── invoice_anomaly.py
├── scripts/
│   ├── train_freight.py
│   └── run_anomaly_detection.py
├── app/
│   └── main.py
├── tests/
│   └── test_api.py
├── artifacts/
├── DATA_DICTIONARY.md
├── requirements.txt
└── README.md
```

## Dataset

The source SQLite database contains purchase, pricing, vendor-invoice and inventory tables. The original database is kept local and is not committed to GitHub because of its large size.

Place the database at the project root as:

```text
 data.db
```

before running the training scripts.

## Run the analysis / ML workflow

```bash
pip install -r requirements.txt
python scripts/train_freight.py
python scripts/run_anomaly_detection.py
```

The scripts recreate the model artifacts under `artifacts/`.

## Notebooks

The repository keeps the original project notebooks close to their original workflow, with only necessary fixes for portability / execution.

- **Freight Prediction.ipynb** — freight-cost modeling workflow
- **invoice flagging.ipynb** — SQL/EDA, rule-based invoice analysis and exploratory classification
- **Inventory_ML_End_to_End.ipynb** — cleaned end-to-end walkthrough of the analytics + ML approach

## Engineering extras

A small FastAPI service, tests and Docker configuration are included as supporting implementation pieces. They are not the main focus of this project; the primary emphasis is **data analytics, SQL/Python analysis and practical ML**.

## Resume-ready description

**Inventory & Vendor Purchase Analytics + ML | Python, SQL, Pandas, scikit-learn**

- Analyzed vendor purchase and invoice data using SQL and Python to study freight costs, payment delays, receiving patterns and unusual transactions.
- Built reusable EDA and feature-engineering workflows from PO-level purchase aggregates and invoice data.
- Developed an ExtraTrees regression model for freight-cost prediction, achieving **R² ≈ 0.98** on a chronological holdout set.
- Applied Isolation Forest for unsupervised invoice anomaly detection without relying on a rule-generated ML target.

## Notes on the original invoice classifier

The original notebook contains a rule-based `flagged_invoice` label and exploratory classification experiments. Those experiments are preserved for reference, but the project does **not** present them as a reliable fraud-prediction model because the target is derived from the same business rules used in the analysis.
