from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_table(table_name: str) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
