# Inventory Management System

A data analysis and machine learning project built around inventory, purchase and vendor invoice data stored in SQLite.

## Project work

### Freight Cost Prediction
- Loaded vendor invoice data from SQLite using Python and Pandas.
- Explored the relationship between invoice value, quantity and freight cost.
- Compared Linear Regression, Decision Tree Regression and Random Forest Regression.
- Evaluated models using MAE, RMSE and R².

### Invoice Flagging
- Used SQL to aggregate purchase-level information and combine it with vendor invoice records.
- Created a rule-based `flagged_invoice` indicator from invoice-value differences and receiving delays.
- Compared flagged and normal invoices using exploratory analysis and statistical tests.
- Experimented with Logistic Regression, Decision Tree and Random Forest classification, followed by Random Forest hyperparameter tuning.

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
└── README.md
```

## Dataset

The SQLite database used for the project is `inventory.db`. It is kept locally and is not committed to GitHub because of its size.

Place `inventory.db` in the project root before running the notebooks or Python scripts.

## Tools

Python · Pandas · NumPy · Matplotlib · Seaborn · SQL · SQLite · scikit-learn · SciPy · Jupyter Notebook
