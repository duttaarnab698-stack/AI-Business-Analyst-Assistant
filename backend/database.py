import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# ============================================================
# LOAD .ENV
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"

DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_NAME = "ai_business_analyst"


if not DB_PASSWORD:
    raise ValueError(
        "DB_PASSWORD not found in .env file."
    )


# ============================================================
# CREATE DATABASE URL SAFELY
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