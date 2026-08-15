import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# PROJECT + ENV
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in .env"
    )


# ============================================================
# CSV
# ============================================================

CSV_FILE = (
    PROJECT_ROOT
    / "data"
    / "superstore.csv"
)

if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"CSV file not found: {CSV_FILE}"
    )


# ============================================================
# ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "connect_timeout": 30
    }
)


# ============================================================
# READ CSV
# ============================================================

print("=" * 60)
print("IMPORTING SUPERSTORE DATA")
print("=" * 60)

print("\nReading:")
print(CSV_FILE)

df = pd.read_csv(
    CSV_FILE,
    encoding="latin1"
)

print("\nCSV loaded successfully.")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
    .str.replace("-", "_", regex=False)
)

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# CLEAN DATE COLUMNS
# ============================================================

df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="coerce"
)

df["ship_date"] = pd.to_datetime(
    df["ship_date"],
    errors="coerce"
)


# ============================================================
# CLEAN NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "row_id",
    "postal_code",
    "sales",
    "quantity",
    "discount",
    "profit"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ============================================================
# DATABASE CONNECTION
# ============================================================

print("\nConnecting to Render PostgreSQL...")

try:

    with engine.connect() as connection:

        connection.execute(
            text("SELECT 1")
        )

    print("Database connection: SUCCESS")

except Exception as error:

    print("\nDatabase connection FAILED:")
    print(error)

    raise


# ============================================================
# REMOVE OLD TABLE
# ============================================================

print("\nRemoving old orders table if it exists...")

try:

    with engine.begin() as connection:

        connection.execute(
            text("DROP TABLE IF EXISTS orders")
        )

    print("Old table removed.")

except Exception as error:

    print("\nCould not remove old table:")
    print(error)

    raise


# ============================================================
# UPLOAD IN SMALL CHUNKS
# ============================================================

print("\nUploading data...")
print("Total rows:", len(df))

CHUNK_SIZE = 250


try:

    first_chunk = True

    total_uploaded = 0


    for start in range(
        0,
        len(df),
        CHUNK_SIZE
    ):

        end = min(
            start + CHUNK_SIZE,
            len(df)
        )


        chunk = df.iloc[
            start:end
        ]


        chunk.to_sql(
            "orders",
            engine,
            if_exists=(
                "replace"
                if first_chunk
                else "append"
            ),
            index=False,
            method=None
        )


        total_uploaded += len(chunk)

        first_chunk = False


        print(
            f"Uploaded: "
            f"{total_uploaded}/{len(df)}"
        )


except Exception as error:

    print("\nIMPORT FAILED:")
    print(error)

    raise


# ============================================================
# VERIFY
# ============================================================

print("\n" + "=" * 60)
print("VERIFYING DATABASE")
print("=" * 60)


try:

    with engine.connect() as connection:

        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM orders"
            )
        )

        total_rows = result.scalar()


    print(
        "\nTotal rows in orders table:",
        total_rows
    )


    if total_rows == len(df):

        print(
            "\nSUCCESS!"
        )

        print(
            f"{total_rows} rows imported successfully."
        )

    else:

        print(
            "\nWARNING:"
        )

        print(
            f"CSV rows: {len(df)}"
        )

        print(
            f"Database rows: {total_rows}"
        )


except Exception as error:

    print("\nVerification failed:")
    print(error)

    raise