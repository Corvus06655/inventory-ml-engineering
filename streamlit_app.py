import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import classification_report, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

st.set_page_config(
    page_title="Inventory & Vendor Intelligence",
    page_icon="📦",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {font-size: 2.2rem; font-weight: 700; margin-bottom: 0.15rem;}
    .subtitle {font-size: 1rem; color: #666; margin-bottom: 1.5rem;}
    .result-card {padding: 1.1rem 1.2rem; border-radius: 12px; border: 1px solid #ddd; margin-top: 1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">📦 Inventory & Vendor Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Freight cost prediction and invoice flagging using the project dataset</div>',
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Database loading
# -----------------------------------------------------------------------------
local_db = Path("inventory.db")
uploaded_db = st.sidebar.file_uploader(
    "Upload inventory.db", type=["db", "sqlite", "sqlite3"]
)


def get_db_path():
    if uploaded_db is not None:
        uploaded_path = Path("uploaded_inventory.db")
        uploaded_path.write_bytes(uploaded_db.getvalue())
        return uploaded_path
    return local_db if local_db.exists() else None


db_path = get_db_path()

st.sidebar.markdown("### Project")
st.sidebar.caption("SQLite → SQL analysis → Python / ML")

if db_path is None:
    st.info(
        "Upload the project's `inventory.db` from the sidebar to use the interactive predictions. "
        "The database is intentionally kept out of GitHub."
    )
    st.stop()


@st.cache_data(show_spinner=False)
def load_vendor_invoice(db_path_str):
    with sqlite3.connect(db_path_str) as conn:
        return pd.read_sql_query("SELECT * FROM vendor_invoice", conn)


@st.cache_data(show_spinner=False)
def load_invoice_analysis(db_path_str):
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
        LEFT JOIN purchase_agg p
            ON p.PONumber = v.PONumber
    """
    with sqlite3.connect(db_path_str) as conn:
        df = pd.read_sql_query(query, conn)

    df["flagged_invoice"] = (
        ((df["invoice_dollars"] - df["total_dollar"]).abs() > 5)
        | (df["avg_receiving_delay"] > 10)
    ).astype(int)
    return df


try:
    vendor_invoice = load_vendor_invoice(str(db_path))
    invoice_df = load_invoice_analysis(str(db_path))
    with sqlite3.connect(str(db_path)) as conn:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", conn
        )["name"].tolist()
except Exception as exc:
    st.error(f"Could not read the SQLite database: {exc}")
    st.stop()

# -----------------------------------------------------------------------------
# Overview
# -----------------------------------------------------------------------------
st.subheader("Project Overview")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Invoice Records", f"{len(vendor_invoice):,}")
m2.metric("Database Tables", f"{len(tables):,}")
m3.metric("Flagged Invoices", f"{int(invoice_df['flagged_invoice'].sum()):,}")
m4.metric("Flag Rate", f"{invoice_df['flagged_invoice'].mean() * 100:.1f}%")

st.caption("Select a section below to interact with the models used in the project notebooks.")

freight_tab, invoice_tab = st.tabs(["🚚 Freight Cost Prediction", "🧾 Invoice Flagging"])

# -----------------------------------------------------------------------------
# Freight cost prediction
# -----------------------------------------------------------------------------
with freight_tab:
    st.subheader("Freight Cost Prediction")
    st.write(
        "Compare three regression models trained on invoice dollars to predict freight cost. "
        "The workflow follows the original project notebook."
    )

    d = vendor_invoice.dropna(subset=["Dollars", "Freight"]).copy()
    X = d[["Dollars"]]
    y = d["Freight"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(max_depth=4, random_state=42),
        "Random Forest": RandomForestRegressor(random_state=42),
    }

    model_results = []
    fitted_models = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        fitted_models[name] = model
        model_results.append(
            {
                "Model": name,
                "MAE": mean_absolute_error(y_test, pred),
                "RMSE": mean_squared_error(y_test, pred) ** 0.5,
                "R²": r2_score(y_test, pred),
            }
        )

    results_df = pd.DataFrame(model_results).sort_values("R²", ascending=False)

    st.markdown("#### Model comparison")
    st.dataframe(
        results_df.style.format(
            {"MAE": "{:.2f}", "RMSE": "{:.2f}", "R²": "{:.3f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Try a prediction")
    left, right = st.columns([1, 1])
    with left:
        selected_model = st.selectbox("Model", list(models.keys()), index=2)
    with right:
        dollars_input = st.number_input(
            "Invoice Dollars", min_value=0.0, value=18500.0, step=500.0
        )

    if st.button("Predict Freight Cost", type="primary", use_container_width=True):
        selected = fitted_models[selected_model]
        prediction = float(selected.predict(pd.DataFrame({"Dollars": [dollars_input]}))[0])
        st.markdown(
            f'<div class="result-card"><b>Predicted Freight Cost</b><br><span style="font-size:2rem;">{prediction:,.2f}</span><br><small>{selected_model}</small></div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### Data relationship")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.scatter(d["Dollars"], d["Freight"], alpha=0.35)
    ax.set_xlabel("Invoice Dollars")
    ax.set_ylabel("Freight")
    ax.set_title("Invoice Value vs Freight Cost")
    ax.grid(alpha=0.15)
    st.pyplot(fig, clear_figure=True)

# -----------------------------------------------------------------------------
# Invoice flagging
# -----------------------------------------------------------------------------
with invoice_tab:
    st.subheader("Invoice Flagging")
    st.write(
        "An invoice is flagged when the invoice amount differs from the associated purchase total by more than 5, "
        "or when average receiving delay is above 10 days."
    )
    st.warning("The flag is rule-based and exploratory; it should not be presented as independent fraud ground truth.")

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
        invoice_quantity = st.number_input(
            "Invoice Quantity", min_value=0.0, value=100.0, step=10.0
        )

    dollar_mismatch = abs(invoice_amount - purchase_total)
    rule_mismatch = dollar_mismatch > 5
    rule_delay = receiving_delay > 10
    flagged = rule_mismatch or rule_delay

    if st.button("Check Invoice", type="primary", use_container_width=True):
        status = "🔴 FLAGGED" if flagged else "🟢 NORMAL"
        st.markdown(
            f'<div class="result-card"><b>Invoice Status</b><br><span style="font-size:2rem;">{status}</span></div>',
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

    st.markdown("#### Classification experiments from the notebook")
    X_cls = invoice_df[
        ["invoice_quantity", "avg_receiving_delay", "Freight", "total_quantity", "total_dollar"]
    ].fillna(0)
    y_cls = invoice_df["flagged_invoice"]

    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X_cls, y_cls, test_size=0.20, random_state=42
    )

    scaler = StandardScaler()
    X_train_c_scaled = scaler.fit_transform(X_train_c)
    X_test_c_scaled = scaler.transform(X_test_c)

    classifiers = {
        "Logistic Regression": LogisticRegression(random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42),
    }

    cls_results = []
    for name, clf in classifiers.items():
        clf.fit(X_train_c_scaled, y_train_c)
        pred = clf.predict(X_test_c_scaled)
        report = classification_report(
            y_test_c, pred, output_dict=True, zero_division=0
        )
        cls_results.append(
            {
                "Model": name,
                "Precision": report["1"]["precision"],
                "Recall": report["1"]["recall"],
                "F1": report["1"]["f1-score"],
            }
        )

    st.dataframe(
        pd.DataFrame(cls_results).style.format(
            {"Precision": "{:.3f}", "Recall": "{:.3f}", "F1": "{:.3f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.caption("Built from the project's original SQLite + Python + scikit-learn workflow.")
