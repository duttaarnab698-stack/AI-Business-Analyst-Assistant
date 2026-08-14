from database import get_data


query = """
SELECT *
FROM orders
LIMIT 10;
"""

df = get_data(query)

print(df)