# Stockwise — Inventory & Vendor Intelligence

> **Turn invoice data into clearer decisions.**

A full-stack inventory and vendor intelligence demo combining a React dashboard with a FastAPI service for freight-cost estimation and rule-based invoice screening.

<p align="center">
  <a href="https://stockwise-react-dashboard.onrender.com/"><strong>🚀 Open the Live Stockwise Dashboard</strong></a>
  &nbsp; · &nbsp;
  <a href="https://inventory-ml-engineering-api.onrender.com/docs">API Swagger Docs</a>
  &nbsp; · &nbsp;
  <a href="https://inventory-ml-engineering-api.onrender.com/health">API Health</a>
</p>

## Live links

| Resource | Link |
| --- | --- |
| **Live React dashboard** | https://stockwise-react-dashboard.onrender.com/ |
| FastAPI interactive docs | https://inventory-ml-engineering-api.onrender.com/docs |
| API health endpoint | https://inventory-ml-engineering-api.onrender.com/health |
| GitHub repository | https://github.com/Corvus06655/inventory-ml-engineering |

## Product sections

The React app is organized as a cinematic landing page plus a dedicated interactive dashboard workspace:

1. **Home / Landing** — warehouse video with poster fallback, live API reachability indicator, project overview and dashboard CTA.
2. **Dashboard Overview** — sample inventory KPIs, throughput chart, priority queue and API status.
3. **Inventory Management** — searchable/filterable sample catalogue, session-only add/restock actions, and CSV export.
4. **Freight Cost Prediction** — sends the entered invoice amount to the real `POST /predict-freight` endpoint.
5. **Invoice Risk Screening** — sends expected/actual totals and receiving delay to the real `POST /validate-invoice` endpoint.
6. **Analytics & Reports** — clearly labelled illustrative trend visualizations and stock summaries.
7. **Technology / How It Works** — explains the actual React, Vite, FastAPI, Python, pandas and scikit-learn stack.
8. **About StockWise** — project purpose, demo limitations and human-review framing.
9. **CTA / Footer** — links to the live dashboard, repository and API documentation.

**Navigation:** The floating lime **Home** control remains available inside the dashboard. The browser Back/Forward buttons also switch between the landing page and dashboard.

## What you can explore

- **Inventory overview:** stock levels, low-stock and out-of-stock signals, vendor summaries and trend visualizations.
- **Inventory table:** search and filter demo items, add an item to the current browser session, and export visible data as CSV.
- **Freight estimator:** send a live request to the deployed FastAPI endpoint using an invoice amount.
- **Invoice screening:** evaluate invoice totals and receiving-delay signals using the project's deterministic business rules.
- **API transparency:** inspect structured results and expand the raw JSON response when needed.
- **Responsive UI:** dashboard layout adapts to desktop and mobile screens.

> **Demo-data notice:** Dashboard inventory rows and trend charts are illustrative demo data. Inventory edits are session-only and are not saved to a persistent database. The freight API may run in synthetic-data demo mode; if so, the returned estimate is illustrative only and must not be used for real purchasing decisions. Check the API response and `/health` endpoint for the active mode.

## Architecture

| Layer | Technology |
| --- | --- |
| Frontend | React, Vite, Recharts, Framer Motion, Lucide |
| API | FastAPI, Pydantic |
| Modeling / analysis | Python, Pandas, scikit-learn |
| Deployment | Render |
| Version control | GitHub |

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | API/model status and data mode |
| GET | `/` | Basic service information |
| POST | `/predict-freight` | Estimate freight from invoice value |
| POST | `/validate-invoice` | Check invoice mismatch and receiving delay |

### Example requests

**Freight prediction**
```json
{
  "invoice_dollars": 18500
}
```

**Invoice screening**
```json
{
  "invoice_dollars": 10000,
  "purchase_total_dollars": 10020,
  "average_receiving_delay_days": 12
}
```

Try the endpoints using the interactive [Swagger UI](https://inventory-ml-engineering-api.onrender.com/docs).

## Run locally

Use Python 3.10+ and Node.js 18+.

### 1. Start the FastAPI backend

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies and start the API:
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs: http://127.0.0.1:8000/docs

### 2. Start the React frontend

Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```

Vite will print the local development URL (usually http://localhost:5173). The frontend uses the deployed API by default. To use a local or alternate API, create `frontend/.env.local` with `VITE_API_URL=http://127.0.0.1:8000` (see `frontend/.env.example`).

### Render frontend deployment

The dashboard is a Render **Static Site** and the API remains the Python web service described in `render.yaml`. The existing `stockwise-react-dashboard` service deploys from `main` on each commit. Its current Render settings are:

| Setting | Value |
| --- | --- |
| Root directory | Repository root (unset) |
| Build command | `cd frontend && npm install && npm run build` |
| Publish directory | `frontend/dist` |
| Optional environment variable | `VITE_API_URL` to override the API host |

`VITE_API_URL` is optional because the deployed API URL is the frontend default. Set it in Render if you use another API host; Vite reads it at build time. These verified service settings are also represented in `render.yaml` so the existing static site can be managed with the project Blueprint. The API's health endpoint is `/health`.

## Original analysis

The repository also contains notebooks and a Streamlit app for freight-model comparison and invoice flag analysis.

- Freight analysis compares Linear Regression, Decision Tree and Random Forest models using MAE, RMSE and R² on an 80/20 train-test split.
- Invoice screening uses business rules: absolute invoice-versus-purchase mismatch greater than 5, or average receiving delay greater than 10 days.
- A rule-based flag is a review signal, not proof of fraud.
- The repository does not claim the previously mentioned R², MAE or RMSE values as verified results.

## Repository structure

```text
inventory-ml-engineering/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── notebook/
│   ├── Freight Prediction.ipynb
│   └── invoice flagging.ipynb
├── freight_cost_prediction/
├── invoice_flagging/
├── main.py
├── render.yaml
├── streamlit_app.py
├── requirements.txt
└── README.md
```

## Limitations and responsible use

- The public demo may use synthetic data because the full local database is not committed.
- The displayed inventory rows and trend chart are sample/demo values; they are not evidence of a live warehouse feed.
- Frontend inventory changes are not persisted.
- Freight predictions from synthetic training data are for demonstration only.
- Invoice flags help prioritize manual review; they do not establish fraud.
- Do not submit confidential vendor, purchase, or invoice information to the public demo.

---

**Live app:** https://stockwise-react-dashboard.onrender.com/
