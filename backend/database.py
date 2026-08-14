import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Local development-এর জন্য .env load করবে
load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "ai_business_analyst")


# ============================================================
# VALIDATE DATABASE CONFIGURATION
# ============================================================

missing = []

if not DB_HOST:
    missing.append("DB_HOST")

if not DB_USER:
    missing.append("DB_USER")

if not DB_PASSWORD:
    missing.append("DB_PASSWORD")

if not DB_NAME:
    missing.append("DB_NAME")


if missing:
    raise ValueError(
        "Missing database environment variables: "
        + ", ".join(missing)
    )


# ============================================================
# CREATE DATABASE URL
# ============================================================

database_url = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)


# ============================================================
# SQLALCHEMY ENGINE
# ============================================================

engine = create_engine(
    database_url,
    pool_pre_ping=True
)


# ============================================================
# TEST CONNECTION
# ============================================================

def test_connection():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            result.fetchone()

        return True

    except Exception as error:

        print("\nDatabase connection failed:")
        print(error)

        return False


# ============================================================
# RUN SQL QUERY
# ============================================================

def get_data(query):

    with engine.connect() as connection:

        df = pd.read_sql(
            text(query),
            connection
        )

    return df


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)

    print("\nHost:", DB_HOST)
    print("Port:", DB_PORT)
    print("User:", DB_USER)
    print("Database:", DB_NAME)

    if test_connection():

        print("\nDatabase connection: SUCCESS")

        query = """
        SELECT COUNT(*) AS total_rows
        FROM orders;
        """

        df = get_data(query)

        print("\nResult:")
        print(df.to_string(index=False))

    else:

        print("\nDatabase connection: FAILED")