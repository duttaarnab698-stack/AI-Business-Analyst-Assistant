"""Optional one-time loader for the Superstore CSV into PostgreSQL orders."""
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from backend.database import engine


def import_orders():
    """Replace the public orders table with the local Superstore dataset."""
    csv_path = Path(__file__).resolve().parent.parent / "data" / "superstore.csv"
    data = pd.read_csv(csv_path, encoding="latin1")
    data.columns = [column.strip().lower().replace(" ", "_").replace("-", "_") for column in data.columns]
    data["order_date"] = pd.to_datetime(data["order_date"], format="%m/%d/%Y").dt.date
    data["ship_date"] = pd.to_datetime(data["ship_date"], format="%m/%d/%Y").dt.date
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS orders"))
        data.to_sql("orders", connection, if_exists="replace", index=False, method="multi")
    return len(data)


if __name__ == "__main__":
    print(f"Imported {import_orders()} rows into PostgreSQL orders.")
