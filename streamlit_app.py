import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

st.set_page_config(page_title="Inventory & Vendor Intelligence", page_icon="📦", layout="wide")

st.markdown(
    """
    <style>
    .main-title {font-size: 2.2rem; font-weight: 700; margin-bottom: 0.15rem;}
    .subtitle {font-size: 1rem; color: #666; margin-bottom: 1.2rem;}
    .result-card {padding: 1.1rem 1.2rem; border-radius: 12px; border: 1px solid #ddd; margin-top: 1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">📦 Inventory & Vendor Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Freight cost prediction and invoice flagging with Python, SQL and scikit-learn</div>',
    unsafe_allow_html=True,
)

# The full project database is intentionally not committed because it is large.
# The public app starts in demo mode and can optionally use the real SQLite DB.
local_db = Path("inventory.db")
uploaded_db = st.sidebar.file_uploader(
    "Use full project database (optional)", type=["db", "sqlite", "sqlite3"]
)


def build_demo_data(seed=42):
    """Create a lightweight representative dataset for the public demo."""
    rng = np.random.default_rng(seed)

    n_freight = 800
    dollars = rng.uniform(500, 30000, n_freight)
    quantity = rng.integers(1, 500, n_freight)
    freight = np.maximum(
        5,
        0.011 * dollars + 0.015 * quantity + rng.normal(0, 35, n_freight),
    )
    vendor_invoice = pd.DataFrame(
        {
            "PONumber": [f"PO{100000 + i}" for i in range(n_freight)],
            "Quantity": quantity,
            "Dollars": dollars,
            "Freight": freight,
        }
    )

    n_invoice = 500
    purchase_total = rng.uniform(1000, 25000, n_invoice)
    mismatch = rng.normal(0, 3, n_invoice)
    deliberate_mismatch = rng.random(n_invoice) < 0.24
    mismatch[deliberate_mismatch] += rng.choice([-1, 1], deliberate_mismatch.sum()) * rng.uniform(
        10, 800, deliberate_mismatch.sum()
    )
    invoice_dollars = np.maximum(0, purchase_total + mismatch)
    receiving_delay = np.maximum(1, rng.normal(7, 4, n_invoice))
    delayed = rng.random(n_invoice) < 0.18
    receiving_delay[delayed] += rng.uniform(5, 15, delayed.sum())

    invoice_df = pd.DataFrame(
        {
            "PONumber": [f"PO{200000 + i}" for i in range(n_invoice)],
            "invoice_quantity": rng.integers(1, 400, n_invoice),
            "invoice_dollars": invoice_dollars,
            "Freight": np.maximum(5, invoice_dollars * 0.011 + rng.normal(0, 30, n_invoice)),
            "days_po_to_invoice": np.maximum(1, receiving_delay + rng.normal(3, 2, n_invoice)),
            "days_to_pay": np.maximum(1, rng.normal(12, 5, n_invoice)),
            "total_dollar": purchase_total,
            "total_brand": rng.integers(1, 8, n_invoice),
            "total_quantity": rng.integers(20, 500, n_invoice),
            "avg_receiving_delay": receiving_delay,
        }
    )
    invoice_df["flagged_invoice"] = (
        ((invoice_df["invoice_dollars"] - invoice_df["total_dollar"]).abs() > 5)
        | (invoice_df["avg_receiving_delay"] > 10)
    ).astype(int)
    return vendor_invoice, invoice_df


def load_real_data(db_path):
    with sqlite3.connect(db_path) as conn:
        vendor_invoice = pd.read_sql_query("SELECT * FROM vendor_invoice", conn)
        query = """
            WITH purchase_agg AS (
                SELECT
                    PONumber,
                    COUNT(DISTINCT Brand) AS total_brand,
                    SUM(Quantity) AS total_quantity,
                    SUM(Dollars) AS total_dollar,
                    AVG(julianday(ReceivingDate) - julianday(PODate)) AS avg_receiving_delay
                FROM purchases
                GROUP BY PONumber
            )
            SELECT
                v.PONumber,
                Quantity AS invoice_quantity,
                Dollars AS invoice_dollars,
                Freight,
                julianday(InvoiceDate) - julianday(PODate) AS days_po_to_invoice,
                julianday(PayDate) - julianday(InvoiceDate) AS days_to_pay,
                total_dollar,
                total_brand,
                total_quantity,
                avg_receiving_delay
            FROM vendor_invoice v
            LEFT JOIN purchase_agg p ON p.PONumber = v.PONumber
        """
        invoice_df = pd.read_sql_query(query, conn)
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", conn
        )["name"].tolist()

    invoice_df["flagged_invoice"] = (
        ((invoice_df["invoice_dollars"] - invoice_df["total_dollar"]).abs() > 5)
        | (invoice_df["avg_receiving_delay"] > 10)
    ).astype(int)
    return vendor_invoice, invoice_df, tables


if uploaded_db is not None:
    uploaded_path = Path("uploaded_inventory.db")
    uploaded_path.write_bytes(uploaded_db.getvalue())
    try:
        vendor_invoice, invoice_df, tables = load_real_data(str(uploaded_path))
        data_mode = "Full project database"
    except Exception as exc:
        st.sidebar.error(f"Could not read database: {exc}")
        vendor_invoice, invoice_df = build_demo_data()
        tables = ["vendor_invoice", "purchases"]
        data_mode = "Demo mode"
else:
    vendor_invoice, invoice_df = build_demo_data()
    tables = ["vendor_invoice", "purchases"]
    data_mode = "Demo mode"

st.sidebar.markdown("### Data source")
st.sidebar.caption(
    "Demo mode uses a small representative dataset so the public page works immediately. "
    "Upload the full inventory.db only when you want to run on the complete project data."
)
st.sidebar.info(data_mode)

st.subheader("Project Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Invoice Records", f"{len(vendor_invoice):,}")
m2.metric("Database Tables", f"{len(tables):,}")
m3.metric("Flagged Invoices", f"{int(invoice_df['flagged_invoice'].sum()):,}")
m4.metric("Flag Rate", f"{invoice_df['flagged_invoice'].mean() * 100:.1f}%")

st.caption("The public demo is ready to use immediately; no database upload is required.")

freight_tab, invoice_tab = st.tabs(["🚚 Freight Cost Prediction", "🧾 Invoice Flagging"])

with freight_tab:
    st.subheader("Freight Cost Prediction")
    st.write(
        "The project compares Linear Regression, Decision Tree and Random Forest models "
        "using invoice dollars to predict freight cost."
    )

    d = vendor_invoice.dropna(subset=["Dollars", "Freight"]).copy()
    X = d[["Dollars"]]
    y = d["Freight"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(max_depth=4, random_state=42),
        "Random Forest": RandomForestRegressor(random_state=42),
    }

    model_results = []
    fitted_models = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        prediction = model.predict(X_test)
        fitted_models[name] = model
        model_results.append(
            {
                "Model": name,
                "MAE": mean_absolute_error(y_test, prediction),
                "RMSE": mean_squared_error(y_test, prediction) ** 0.5,
                "R²": r2_score(y_test, prediction),
            }
        )

    results_df = pd.DataFrame(model_results).sort_values("R²", ascending=False)
    st.markdown("#### Model comparison")
    st.dataframe(
        results_df.style.format({"MAE": "{:.2f}", "RMSE": "{:.2f}", "R²": "{:.3f}"}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Try a prediction")
    left, right = st.columns(2)
    with left:
        selected_model = st.selectbox("Model", list(models.keys()), index=2)
    with right:
        dollars_input = st.number_input("Invoice Dollars", min_value=0.0, value=18500.0, step=500.0)

    if st.button("Predict Freight Cost", type="primary", use_container_width=True):
        model = fitted_models[selected_model]
        prediction = float(model.predict(pd.DataFrame({"Dollars": [dollars_input]}))[0])
        st.markdown(
            f'<div class="result-card"><b>Predicted Freight Cost</b><br>'
            f'<span style="font-size:2rem;">{prediction:,.2f}</span><br>'
            f'<small>{selected_model} • {data_mode}</small></div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### Invoice value vs freight")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.scatter(d["Dollars"], d["Freight"], alpha=0.35)
    ax.set_xlabel("Invoice Dollars")
    ax.set_ylabel("Freight")
    ax.set_title("Invoice Value vs Freight Cost")
    ax.grid(alpha=0.15)
    st.pyplot(fig, clear_figure=True)

with invoice_tab:
    st.subheader("Invoice Flagging")
    st.write(
        "The project flags invoices when the invoice amount differs from the associated purchase total by more than 5, "
        "or when average receiving delay is above 10 days."
    )
    st.warning("This is a rule-based exploratory flag, not independent fraud ground truth.")

    st.markdown("#### Check an invoice")
    a, b = st.columns(2)
    with a:
        invoice_amount = st.number_input(
            "Invoice Dollars", min_value=0.0, value=10000.0, step=100.0, key="invoice_amount"
        )
        purchase_total = st.number_input(
            "Purchase Total Dollars", min_value=0.0, value=10000.0, step=100.0
        )
    with b:
        receiving_delay = st.number_input(
            "Average Receiving Delay (days)", min_value=0.0, value=5.0, step=1.0
        )
        st.caption("The rule-based flag uses invoice amount mismatch and receiving delay.")

    dollar_mismatch = abs(invoice_amount - purchase_total)
    rule_mismatch = dollar_mismatch > 5
    rule_delay = receiving_delay > 10
    flagged = rule_mismatch or rule_delay

    if st.button("Check Invoice", type="primary", use_container_width=True):
        status = "🔴 FLAGGED" if flagged else "🟢 NORMAL"
        st.markdown(
            f'<div class="result-card"><b>Invoice Status</b><br>'
            f'<span style="font-size:2rem;">{status}</span></div>',
            unsafe_allow_html=True,
        )

        reasons = []
        if rule_mismatch:
            reasons.append(f"Dollar mismatch is {dollar_mismatch:,.2f} (> 5)")
        if rule_delay:
            reasons.append(f"Average receiving delay is {receiving_delay:.1f} days (> 10)")
        if not reasons:
            reasons.append("No project rule was triggered")

        st.markdown("**Rule evaluation**")
        for reason in reasons:
            st.write(f"• {reason}")

    st.markdown("#### Project-level invoice analysis")
    c1, c2, c3 = st.columns(3)
    c1.metric("Invoices", f"{len(invoice_df):,}")
    c2.metric("Flagged", f"{int(invoice_df['flagged_invoice'].sum()):,}")
    c3.metric("Flag Rate", f"{invoice_df['flagged_invoice'].mean() * 100:.1f}%")

    show_rows = st.slider("Rows to preview", min_value=5, max_value=30, value=10, step=5)
    preview = invoice_df[
        [
            "PONumber",
            "invoice_quantity",
            "invoice_dollars",
            "Freight",
            "days_po_to_invoice",
            "days_to_pay",
            "total_dollar",
            "avg_receiving_delay",
            "flagged_invoice",
        ]
    ].head(show_rows)
    st.dataframe(preview, use_container_width=True, hide_index=True)

st.divider()
st.caption("Built from the project's original SQLite + Python + scikit-learn workflow. Public demo data is representative, not the full 400+ MB database.")
