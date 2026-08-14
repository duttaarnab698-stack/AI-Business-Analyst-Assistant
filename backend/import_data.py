import pandas as pd
import mysql.connector


# ==============================
# 1. Read CSV
# ==============================

df = pd.read_csv(
    "data/superstore.csv",
    encoding="latin1"
)

# Convert column names to lowercase
df.columns = [
    col.strip().lower().replace(" ", "_").replace("-", "_")
    for col in df.columns
]


# ==============================
# 2. Convert dates
# ==============================

df["order_date"] = pd.to_datetime(
    df["order_date"],
    format="%m/%d/%Y"
).dt.date

df["ship_date"] = pd.to_datetime(
    df["ship_date"],
    format="%m/%d/%Y"
).dt.date


# ==============================
# 3. Connect to MySQL
# ==============================

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arnab@2005",
    database="ai_business_analyst"
)

cursor = connection.cursor()


# ==============================
# 4. Insert query
# ==============================

query = """
INSERT INTO orders (
    row_id,
    order_id,
    order_date,
    ship_date,
    ship_mode,
    customer_id,
    customer_name,
    segment,
    country,
    city,
    state,
    postal_code,
    region,
    product_id,
    category,
    sub_category,
    product_name,
    sales,
    quantity,
    discount,
    profit
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""


# ==============================
# 5. Convert DataFrame to records
# ==============================

data = []

for _, row in df.iterrows():
    data.append((
        int(row["row_id"]),
        row["order_id"],
        row["order_date"],
        row["ship_date"],
        row["ship_mode"],
        row["customer_id"],
        row["customer_name"],
        row["segment"],
        row["country"],
        row["city"],
        row["state"],
        str(row["postal_code"]),
        row["region"],
        row["product_id"],
        row["category"],
        row["sub_category"],
        row["product_name"],
        float(row["sales"]),
        int(row["quantity"]),
        float(row["discount"]),
        float(row["profit"])
    ))


# ==============================
# 6. Insert all records
# ==============================

cursor.executemany(query, data)

connection.commit()

print(f"Successfully inserted {cursor.rowcount} rows.")


# ==============================
# 7. Close connection
# ==============================

cursor.close()
connection.close()

print("Database connection closed.")