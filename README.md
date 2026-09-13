# Inventory & Vendor Intelligence

A data analytics and machine learning project built from a SQLite inventory and vendor dataset. The project explores vendor purchases, invoice behavior and freight costs using Python, SQL, Pandas, scikit-learn and Streamlit.

## Project overview

### Freight Cost Prediction

The freight notebook analyzes relationships between invoice value, quantity and freight cost, then compares three regression models:

- Linear Regression
- Decision Tree Regressor
- Random Forest Regressor

The target is `Freight` and the main predictive input used in the notebook is `Dollars`. Models are evaluated with MAE, MSE/RMSE and R² using an 80/20 train-test split.

### Invoice Flagging

The invoice workflow combines purchase-level aggregates with vendor invoices using SQL. It creates a rule-based `flagged_invoice` indicator when the invoice amount differs materially from the purchase total or the average receiving delay is above 10 days.

The notebook then compares Logistic Regression, Decision Tree and Random Forest classifiers and performs Random Forest hyperparameter tuning with F1 score as the selection metric.

The rule-generated flag is treated as an exploratory business label, not as independent fraud ground truth.

## Streamlit app

`streamlit_app.py` provides a small interactive interface for the same project workflows. Upload `inventory.db` in the sidebar to run the analysis without committing the large local database to GitHub.

Run locally with:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app includes:

- freight model comparison and interactive freight prediction
- invoice flag distribution and flagged-record preview
- classification comparison and Random Forest feature importance

## Repository structure

```text
inventory-ml-engineering/
├── notebook/
│   ├── Freight Prediction.ipynb
│   └── invoice flagging.ipynb
├── freight_cost_prediction/
│   ├── data_preprocessing.py
│   └── model_evaluation.py
├── invoice_flagging/
│   ├── data_preprocessing.py
│   ├── modeling_evaluation.py
│   └── train.py
├── streamlit_app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Dataset

The project uses `inventory.db` locally. The database is intentionally not committed to GitHub because of its size. Place it at the project root when running the notebooks locally, or upload it through the Streamlit app.

## Notes

The notebooks are the original project workflow. The Python modules contain the supporting preprocessing and model-evaluation functions used during development. Streamlit is used only as the presentation/deployment layer; no Docker setup is required.
