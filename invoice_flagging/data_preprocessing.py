import os
import sqlite3
import pandas as pd
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = os.getenv("INVOICE_DB_PATH", str(ROOT / "inventory.db"))


def load_data(db_path=DB_PATH):
    """Load and prepare the invoice-level dataset from SQLite."""
    conn = sqlite3.connect(db_path)

    query = """
    WITH purchase_agg AS (
        SELECT
            PONumber,
            COUNT(DISTINCT Brand) AS total_brand,
            SUM(Quantity) AS total_quantity,
            SUM(Dollars) AS total_dollar,
            AVG(
                julianday(ReceivingDate) - julianday(PODate)
            ) AS avg_receving_dely
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
        avg_receving_dely
    FROM vendor_invoice v
    LEFT JOIN purchase_agg p
        ON p.PONumber = v.PONumber
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def invoice_risk(row):
    """Create the rule-based invoice flag used as the target."""
    if abs(row["invoice_dollars"] - row["total_dollar"]) > 5:
        return 1

    if row["avg_receving_dely"] > 10:
        return 1

    return 0


def prepare_data(db_path=DB_PATH):
    """Load data and create the flagged_invoice target."""
    df = load_data(db_path)
    df["flagged_invoice"] = df.apply(invoice_risk, axis=1)
    return df


if __name__ == "__main__":
    df = prepare_data()
    print("Dataset shape:", df.shape)
    print("\nMissing values:")
    print(df.isnull().sum())
    print("\nInvoice flag distribution:")
    print(df["flagged_invoice"].value_counts())
    print("\nColumns:")
    print(df.columns.tolist())
