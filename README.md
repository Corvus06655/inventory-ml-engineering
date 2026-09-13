# Inventory & Vendor Intelligence

A data analytics and machine learning project built from a SQLite inventory and vendor dataset. The project explores vendor purchases, invoice behavior and freight costs using Python, SQL, Pandas and scikit-learn.

## Results at a glance

| Area | Approach | Evaluation |
| --- | --- | --- |
| Freight cost prediction | Linear Regression, Decision Tree, Random Forest | MAE, RMSE, R² on an 80/20 train-test split |
| Invoice flagging | SQL-derived business rules | Dollar mismatch > 5 or average receiving delay > 10 days |

> **Important:** The repository does not claim ExtraTrees, Isolation Forest, or a chronological holdout for this project because those methods are not part of the current original workflow. The numbers `R² = 0.984`, `MAE = 44.22`, and `RMSE = 108.74` should therefore not be presented as this project's verified results.

## Project overview

### Freight Cost Prediction

The freight notebook analyzes relationships between invoice value, quantity and freight cost, then compares three regression models:

- Linear Regression
- Decision Tree Regressor
- Random Forest Regressor

The target is `Freight` and the main predictive input used in the notebook is `Dollars`. Models are evaluated with MAE, RMSE and R² using an 80/20 train-test split.

### Invoice Flagging

The invoice workflow combines purchase-level aggregates with vendor invoices using SQL. It creates a rule-based `flagged_invoice` indicator when the invoice amount differs from the purchase total by more than 5 or the average receiving delay is above 10 days.

The notebook also contains exploratory classification experiments using Logistic Regression, Decision Tree and Random Forest. These are **not treated as validated fraud models**, because the classification target is itself derived from the business rules above.

> **Why not use the rule-derived label as ground truth?** Training a classifier against a label created by the same rules can reproduce those rules rather than independently learn fraud or invoice-risk behavior. For this project, the rule-based flag is therefore kept as an exploratory business indicator instead of being presented as independent fraud ground truth.

## Business impact

The analysis turns raw purchase and invoice records into two practical workflows: estimating freight cost from invoice value and prioritizing invoice exceptions for further review. The invoice rules are designed as screening signals, not as proof of fraud.

## Visuals

The Streamlit app provides the interactive project view, including the freight-value relationship, model comparison and invoice-flag analysis. The repository intentionally does not publish fabricated feature-importance or anomaly-score plots: those visuals should be generated from verified project data before being presented as results.

## Streamlit app

`streamlit_app.py` provides a lightweight interactive presentation layer for the same project workflows. The public demo starts in demo mode so a 400+ MB local database is not required. The full `inventory.db` can still be uploaded when running the app against the complete project data.

Run locally with:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app includes:

- freight model comparison and interactive freight prediction
- invoice flagging using the project's business rules
- project-level invoice analysis and exploratory classification comparison

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

## Reproducibility

Dependencies are listed in `requirements.txt`. The project database is intentionally not committed to GitHub because of its size. Place `inventory.db` at the project root when running the notebooks locally, or upload it through the Streamlit app to run the full workflow.

## Notes

The notebooks are the original project workflow. The Python modules contain the supporting preprocessing and model-evaluation functions used during development. Streamlit is used only as the presentation/deployment layer; no Docker setup is required.
