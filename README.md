# Inventory & Vendor Intelligence

A data analytics and machine learning project built around inventory purchases, vendor invoices and freight costs using Python, SQL, Pandas and scikit-learn. It includes a Streamlit interface and a FastAPI service for freight-cost estimation and rule-based invoice screening.

## Project capabilities

| Area | Approach | Evaluation / rule |
| --- | --- | --- |
| Freight cost prediction | Linear Regression, Decision Tree, Random Forest in the original analysis | MAE, RMSE and R² on an 80/20 train-test split |
| Invoice flagging | SQL-derived business rules | Dollar mismatch > 5 or average receiving delay > 10 days |
| REST API | FastAPI + Pydantic validation | Interactive OpenAPI docs at `/docs` |

> **Results integrity:** The repository does not claim ExtraTrees, Isolation Forest, or a chronological holdout for the original project workflow. The numbers `R² = 0.984`, `MAE = 44.22`, and `RMSE = 108.74` should not be presented as verified results.
>
> The invoice flag is a rule-based screening signal, not independent fraud ground truth. A flag is not proof of fraud.

## Freight cost prediction

The original notebook compares Linear Regression, Decision Tree Regressor and Random Forest Regressor. The target is `Freight`, with `Dollars` as the main predictive input. The notebook evaluates models using MAE, RMSE and R² with an 80/20 train-test split.

## Invoice flagging

The invoice workflow combines purchase-level aggregates with vendor invoices using SQL. It flags an invoice when the absolute difference between invoice dollars and the associated purchase total exceeds 5, or when average receiving delay exceeds 10 days. These rules prioritize records for review; they do not establish fraud.

## Live API (FastAPI)

The API exposes two workflows:

- `POST /predict-freight` — estimates freight from invoice value.
- `POST /validate-invoice` — checks invoice-total mismatch and receiving delay against the project's rules.
- `GET /health` — reports service/model status and whether the API is using the local database or demo data.
- `GET /` — basic service information.

### Run locally

Use Python 3.10 or newer (recommended).

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to try the endpoints interactively. Health status is available at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

### Example requests

Freight prediction:

```json
{
  "invoice_dollars": 18500
}
```

Invoice screening:

```json
{
  "invoice_dollars": 10000,
  "purchase_total_dollars": 10020,
  "average_receiving_delay_days": 12
}
```

### Data and deployment notes

- If a compatible `inventory.db` file is present at the repository root and contains at least 10 valid `vendor_invoice` rows with `Dollars` and `Freight`, the API trains its freight estimator from that data at startup.
- The database is intentionally not committed because of its size. If it is absent, the API uses reproducible **synthetic demo data** so the service can still start. In demo mode, freight estimates are illustrative only and must not be used for real purchasing decisions.
- The API fits a lightweight Random Forest on startup for demonstration. It is not a saved, independently validated production model. Validate generalization, units, and business suitability before operational use.
- Invoice validation is deterministic business-rule logic and does not require a database.
- No real database or credentials are required for the public demo.

### Deploy to Render

This repository includes `render.yaml` for a basic Render web service configuration. Connect the GitHub repository in Render and deploy using the detected Blueprint configuration. After deployment, use the service's `/docs` URL to test it.

The public deployment uses synthetic data unless you separately configure access to a compatible database. Do not upload confidential vendor or invoice data to a public demo service.

## Streamlit app

`streamlit_app.py` provides the interactive project view, including freight-model comparison and invoice flag analysis. The public app starts in demo mode so the large local database is not required.

Run locally:

```bash
streamlit run streamlit_app.py
```

The app can optionally accept the full `inventory.db` file through its sidebar uploader.

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
├── main.py
├── render.yaml
├── streamlit_app.py
├── requirements.txt
└── README.md
```

## Reproducibility

Dependencies are listed in `requirements.txt`. The full project database is intentionally not committed to GitHub because of its size. Place `inventory.db` at the project root for the API/notebooks to use the complete data workflow, or use the built-in synthetic demo mode to explore the API without private or large data files.
