import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# =========================
# AIVEN MYSQL CONNECTION
# =========================
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("Database environment variables are missing.")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# =========================
# READ CSV
# =========================
CSV_FILE = "data/superstore.csv"

df = pd.read_csv(
    CSV_FILE,
    encoding="latin1"
)

print(f"CSV loaded: {len(df)} rows")

# =========================
# CLEAN COLUMN NAMES
# =========================
df.columns = [
    col.strip().lower().replace(" ", "_").replace("-", "_")
    for col in df.columns
]

# =========================
# DATE CONVERSION
# =========================
def convert_date(value):
    if pd.isna(value):
        return pd.NaT

    value = str(value).strip()

    # YYYY-MM-DD
    if len(value) >= 10 and value[4] == "-":
        return pd.to_datetime(
            value[:10],
            format="%Y-%m-%d",
            errors="coerce"
        )

    # MM/DD/YYYY or MM-DD-YYYY
    value = value.replace("-", "/")

    return pd.to_datetime(
        value,
        format="%m/%d/%Y",
        errors="coerce"
    )


df["order_date"] = df["order_date"].apply(convert_date)
df["ship_date"] = df["ship_date"].apply(convert_date)

# =========================
# CREATE TABLE
# =========================
create_table_sql = """
CREATE TABLE IF NOT EXISTS orders (
    row_id INT PRIMARY KEY,
    order_id VARCHAR(50),
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(50),
    customer_id VARCHAR(50),
    customer_name VARCHAR(150),
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50),
    product_id VARCHAR(50),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    product_name VARCHAR(255),
    sales DECIMAL(12,2),
    quantity INT,
    discount DECIMAL(8,4),
    profit DECIMAL(12,2)
)
"""

with engine.begin() as connection:
    connection.execute(text(create_table_sql))

print("Orders table ready.")

# =========================
# IMPORT DATA
# =========================
df.to_sql(
    "orders",
    con=engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=500
)

print("================================")
print("DATA IMPORT SUCCESSFUL!")
print("Rows imported:", len(df))
print("================================")