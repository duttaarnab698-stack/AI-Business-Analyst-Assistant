import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


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
# NORMALIZE THE URL FOR PSYCOPG
# ============================================================

try:
    database_url = make_url(DATABASE_URL)
except Exception as error:
    raise ValueError("DATABASE_URL must be a valid PostgreSQL URL.") from error

if database_url.drivername not in {
    "postgresql",
    "postgres",
    "postgresql+psycopg",
}:
    raise ValueError(
        "DATABASE_URL must use postgresql://, postgres://, "
        "or postgresql+psycopg://."
    )

# URL.set preserves encoded credentials and query parameters while selecting the
# installed psycopg (v3) dialect.  It is safer than modifying the raw URL string.
DATABASE_URL = database_url.set(drivername="postgresql+psycopg")


# ============================================================
# SSL OPTIONS
# ============================================================

# A provider-supplied SSL option in the URL is authoritative.  Otherwise require
# TLS explicitly for hosted PostgreSQL.  This avoids duplicate/conflicting
# sslmode values between the URL and psycopg connect arguments.
SSL_QUERY_PARAMETERS = {
    "sslmode",
    "sslrootcert",
    "sslcert",
    "sslkey",
    "sslcrl",
}

connect_args = {
    "connect_timeout": 10,
}

if not SSL_QUERY_PARAMETERS.intersection(database_url.query):
    connect_args["sslmode"] = "require"


# ============================================================
# POSTGRESQL ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=1,
    max_overflow=0,
    pool_recycle=300,
    pool_timeout=10,
    connect_args=connect_args,
)


def dispose_engine():
    """Close idle pooled connections when a serverless request is complete."""
    engine.dispose()


# ============================================================
# TEST CONNECTION
# ============================================================

def test_connection():
    try:
        # This checks a real connection and a simple PostgreSQL round trip.
        with engine.connect() as connection:
            return connection.scalar(text("SELECT 1")) == 1
    except Exception as error:
        print("\nDatabase connection failed:")
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
