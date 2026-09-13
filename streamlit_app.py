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

st.set_page_config(page_title="Inventory & Vendor Intelligence", page_icon="📦", layout="wide")

st.title("📦 Inventory & Vendor Intelligence")
st.caption("SQL + Python analytics for freight costs and invoice flagging")

st.sidebar.header("Data")
uploaded_db = st.sidebar.file_uploader("Upload inventory.db", type=["db", "sqlite", "sqlite3"])
local_db = Path("inventory.db")


def get_db_path():
    if uploaded_db is not None:
        temp_path = Path("uploaded_inventory.db")
        temp_path.write_bytes(uploaded_db.getvalue())
        return temp_path
    if local_db.exists():
        return local_db
    return None


db_path = get_db_path()

if db_path is None:
    st.info("Upload the project's inventory.db from the sidebar to run the dashboard. The database is kept out of the repository because of its size.")
    st.stop()


@st.cache_data(show_spinner=False)
def load_table(db_path_str, table_name):
    with sqlite3.connect(db_path_str) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)


@st.cache_data(show_spinner=False)
def load_invoice_analysis(db_path_str):
    with sqlite3.connect(db_path_str) as conn:
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
        df = pd.read_sql_query(query, conn)

    df["flagged_invoice"] = (
        ((df["invoice_dollars"] - df["total_dollar"]).abs() > 5)
        | (df["avg_receiving_delay"] > 10)
    ).astype(int)
    return df


try:
    vendor_invoice = load_table(str(db_path), "vendor_invoice")
    with sqlite3.connect(str(db_path)) as conn:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", conn
        )["name"].tolist()
except Exception as exc:
    st.error(f"Could not read the SQLite database: {exc}")
    st.stop()

st.sidebar.success(f"Connected: {len(tables)} tables")

with st.expander("Available tables"):
    st.write(tables)

freight_tab, invoice_tab = st.tabs(["Freight Cost Prediction", "Invoice Flagging"])

with freight_tab:
    st.subheader("Freight Cost Prediction")
    st.write(
        "The notebook compares Linear Regression, Decision Tree and Random Forest "
        "models using invoice dollars to predict freight cost."
    )

    d = vendor_invoice.dropna(subset=["Dollars", "Freight"]).copy()
    X = d[["Dollars"]]
    y = d["Freight"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(max_depth=4, random_state=42),
        "Random Forest": RandomForestRegressor(random_state=42),
    }

    results = []
    fitted = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        fitted[name] = model
        results.append(
            {
                "Model": name,
                "MAE": mean_absolute_error(y_test, pred),
                "RMSE": mean_squared_error(y_test, pred) ** 0.5,
                "R²": r2_score(y_test, pred),
            }
        )

    results_df = pd.DataFrame(results).sort_values("R²", ascending=False)
    st.dataframe(
        results_df.style.format({"MAE": "{:.2f}", "RMSE": "{:.2f}", "R²": "{:.3f}"}),
        use_container_width=True,
    )

    selected = st.selectbox("Model", list(models.keys()), index=2)
    model = fitted[selected]
    prediction_input = st.number_input(
        "Invoice Dollars", min_value=0.0, value=18500.0, step=500.0
    )
    if st.button("Predict Freight", type="primary"):
        prediction = float(model.predict(pd.DataFrame({"Dollars": [prediction_input]}))[0])
        st.metric("Predicted Freight", f"{prediction:,.2f}")

    st.subheader("Dollars vs Freight")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(d["Dollars"], d["Freight"], alpha=0.35)
    ax.set_xlabel("Dollars")
    ax.set_ylabel("Freight")
    ax.set_title("Invoice Value vs Freight Cost")
    st.pyplot(fig, clear_figure=True)

with invoice_tab:
    st.subheader("Invoice Flagging")
    st.write(
        "Invoices are flagged with the same business rules used in the notebook: "
        "dollar mismatch greater than 5 or average receiving delay above 10 days."
    )
    st.warning("The flag is rule-based and exploratory; it is not independent fraud ground truth.")

    df = load_invoice_analysis(str(db_path))
    col1, col2, col3 = st.columns(3)
    col1.metric("Invoices", f"{len(df):,}")
    col2.metric("Flagged", f"{int(df['flagged_invoice'].sum()):,}")
    col3.metric("Flag Rate", f"{df['flagged_invoice'].mean() * 100:.1f}%")

    st.dataframe(df.head(20), use_container_width=True)

    X = df[
        ["invoice_quantity", "avg_receiving_delay", "Freight", "total_quantity", "total_dollar"]
    ].fillna(0)
    y = df["flagged_invoice"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    classifiers = {
        "Logistic Regression": LogisticRegression(random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42),
    }

    clf_results = []
    rf_model = None
    for name, clf in classifiers.items():
        clf.fit(X_train_scaled, y_train)
        pred = clf.predict(X_test_scaled)
        report = classification_report(y_test, pred, output_dict=True, zero_division=0)
        clf_results.append(
            {
                "Model": name,
                "Precision": report["1"]["precision"],
                "Recall": report["1"]["recall"],
                "F1": report["1"]["f1-score"],
            }
        )
        if name == "Random Forest":
            rf_model = clf

    st.subheader("Classification comparison")
    st.dataframe(
        pd.DataFrame(clf_results).style.format(
            {"Precision": "{:.3f}", "Recall": "{:.3f}", "F1": "{:.3f}"}
        ),
        use_container_width=True,
    )

    if rf_model is not None:
        importance = pd.DataFrame(
            {"Feature": X.columns, "Importance": rf_model.feature_importances_}
        ).sort_values("Importance", ascending=False)
        st.subheader("Random Forest feature importance")
        st.bar_chart(importance.set_index("Feature"))
