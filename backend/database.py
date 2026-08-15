import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# LOAD .ENV
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# DATABASE URL
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is required. Set it in Vercel environment variables or .env for local development.")


# ============================================================
# FORCE PSYCOPG DRIVER
# ============================================================

if DATABASE_URL.startswith("postgresql://"):

    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )

elif DATABASE_URL.startswith("postgres://"):

    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1
    )

elif DATABASE_URL.startswith("postgresql+psycopg2://"):

    DATABASE_URL = DATABASE_URL.replace(
        "postgresql+psycopg2://",
        "postgresql+psycopg://",
        1
    )

elif not DATABASE_URL.startswith("postgresql+psycopg://"):
    raise ValueError("DATABASE_URL must use a PostgreSQL URL (postgresql://, postgres://, or postgresql+psycopg://).")


# ============================================================
# POSTGRESQL ENGINE
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

        print(
            "\nDatabase connection failed:"
        )

        print(error)

        return False


# ============================================================
# RUN SQL QUERY
# ============================================================

def get_data(query):

    try:

        with engine.connect() as connection:

            df = pd.read_sql(
                text(query),
                connection
            )

        return df

    except Exception as error:

        print(
            "\nDatabase query failed:"
        )

        print(error)

        raise


# ============================================================
# CHECK ORDERS TABLE
# ============================================================

def check_orders_table():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'orders'
                """)
            )

            return result.scalar() > 0

    except Exception as error:

        print(
            "\nTable check failed:"
        )

        print(error)

        return False


# ============================================================
# GET TOTAL ROWS
# ============================================================

def get_total_rows():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM orders
                """)
            )

            return result.scalar()

    except Exception as error:

        print(
            "\nRow count failed:"
        )

        print(error)

        return None


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "POSTGRESQL DATABASE CONNECTION TEST"
    )

    print("=" * 60)


    print(
        "\nDatabase URL: Loaded from .env"
    )


    # ========================================================
    # CONNECTION TEST
    # ========================================================

    if test_connection():

        print(
            "\nDatabase connection: SUCCESS"
        )


        # ====================================================
        # ORDERS TABLE TEST
        # ====================================================

        if check_orders_table():

            print(
                "\norders table: EXISTS"
            )


            # =================================================
            # ROW COUNT
            # =================================================

            total_rows = get_total_rows()


            print(
                "\nTotal rows:"
            )

            print(
                total_rows
            )


            # =================================================
            # FINAL STATUS
            # =================================================

            if total_rows == 9994:

                print(
                    "\nSUCCESS: "
                    "All 9994 rows are available."
                )

            else:

                print(
                    "\nWARNING: "
                    f"Expected 9994 rows, "
                    f"but found {total_rows}."
                )


        else:

            print(
                "\norders table: NOT FOUND"
            )

            print(
                "Please import superstore.csv first."
            )


    else:

        print(
            "\nDatabase connection: FAILED"
        )
