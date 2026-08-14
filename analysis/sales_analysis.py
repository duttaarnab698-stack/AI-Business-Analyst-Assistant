from backend.database import get_data


def show(title, df):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print(df.to_string(index=False))


# ============================================================
# 1. OVERALL BUSINESS KPIs
# ============================================================

query = """
SELECT
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(quantity) AS total_quantity
FROM orders;
"""

df = get_data(query)
show("OVERALL BUSINESS KPIs", df)


# ============================================================
# 2. MONTHLY SALES & PROFIT TREND
# ============================================================

query = """
SELECT
    YEAR(order_date) AS year,
    MONTH(order_date) AS month,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders
GROUP BY YEAR(order_date), MONTH(order_date)
ORDER BY year, month;
"""

df = get_data(query)
show("MONTHLY SALES & PROFIT TREND", df)


# ============================================================
# 3. CATEGORY ANALYSIS
# ============================================================

query = """
SELECT
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity
FROM orders
GROUP BY category
ORDER BY total_sales DESC;
"""

df = get_data(query)
show("CATEGORY ANALYSIS", df)


# ============================================================
# 4. SUB-CATEGORY ANALYSIS
# ============================================================

query = """
SELECT
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity
FROM orders
GROUP BY sub_category
ORDER BY total_sales DESC;
"""

df = get_data(query)
show("SUB-CATEGORY ANALYSIS", df)


# ============================================================
# 5. REGION ANALYSIS
# ============================================================

query = """
SELECT
    region,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity
FROM orders
GROUP BY region
ORDER BY total_sales DESC;
"""

df = get_data(query)
show("REGION ANALYSIS", df)


# ============================================================
# 6. SEGMENT ANALYSIS
# ============================================================

query = """
SELECT
    segment,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT customer_id) AS customers
FROM orders
GROUP BY segment
ORDER BY total_sales DESC;
"""

df = get_data(query)
show("CUSTOMER SEGMENT ANALYSIS", df)


# ============================================================
# 7. FEBRUARY vs MARCH — ALL YEARS
# ============================================================

query = """
SELECT
    MONTH(order_date) AS month,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders
WHERE MONTH(order_date) IN (2, 3)
GROUP BY MONTH(order_date)
ORDER BY month;
"""

df = get_data(query)
show("FEBRUARY vs MARCH", df)


# ============================================================
# 8. MARCH SALES & PROFIT
# ============================================================

query = """
SELECT
    ROUND(SUM(sales), 2) AS march_sales,
    ROUND(SUM(profit), 2) AS march_profit,
    SUM(quantity) AS march_quantity,
    COUNT(DISTINCT order_id) AS march_orders
FROM orders
WHERE MONTH(order_date) = 3;
"""

df = get_data(query)
show("MARCH PERFORMANCE", df)


# ============================================================
# 9. FEBRUARY → MARCH SALES CHANGE %
# ============================================================

query = """
SELECT
    ROUND(
        (
            SUM(CASE WHEN MONTH(order_date) = 3 THEN sales ELSE 0 END)
            -
            SUM(CASE WHEN MONTH(order_date) = 2 THEN sales ELSE 0 END)
        )
        /
        NULLIF(
            SUM(CASE WHEN MONTH(order_date) = 2 THEN sales ELSE 0 END),
            0
        ) * 100,
        2
    ) AS sales_change_percentage
FROM orders;
"""

df = get_data(query)
show("FEBRUARY → MARCH SALES CHANGE %", df)


# ============================================================
# 10. CATEGORY: FEBRUARY vs MARCH
# ============================================================

query = """
SELECT
    category,

    ROUND(
        SUM(CASE
            WHEN MONTH(order_date) = 2
            THEN sales ELSE 0
        END), 2
    ) AS february_sales,

    ROUND(
        SUM(CASE
            WHEN MONTH(order_date) = 3
            THEN sales ELSE 0
        END), 2
    ) AS march_sales,

    ROUND(
        SUM(CASE
            WHEN MONTH(order_date) = 3
            THEN sales ELSE 0
        END)
        -
        SUM(CASE
            WHEN MONTH(order_date) = 2
            THEN sales ELSE 0
        END),
        2
    ) AS sales_change

FROM orders
WHERE MONTH(order_date) IN (2, 3)
GROUP BY category
ORDER BY sales_change ASC;
"""

df = get_data(query)
show("CATEGORY: FEBRUARY vs MARCH", df)


# ============================================================
# 11. REGION: FEBRUARY vs MARCH
# ============================================================

query = """
SELECT
    region,

    ROUND(
        SUM(CASE
            WHEN MONTH(order_date) = 2
            THEN sales ELSE 0
        END), 2
    ) AS february_sales,

    ROUND(
        SUM(CASE
            WHEN MONTH(order_date) = 3
            THEN sales ELSE 0
        END), 2
    ) AS march_sales,

    ROUND(
        SUM(CASE
            WHEN MONTH(order_date) = 3
            THEN sales ELSE 0
        END)
        -
        SUM(CASE
            WHEN MONTH(order_date) = 2
            THEN sales ELSE 0
        END),
        2
    ) AS sales_change

FROM orders
WHERE MONTH(order_date) IN (2, 3)
GROUP BY region
ORDER BY sales_change ASC;
"""

df = get_data(query)
show("REGION: FEBRUARY vs MARCH", df)


# ============================================================
# 12. TOP 10 CUSTOMERS
# ============================================================

query = """
SELECT
    customer_id,
    customer_name,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM orders
GROUP BY customer_id, customer_name
ORDER BY total_sales DESC
LIMIT 10;
"""

df = get_data(query)
show("TOP 10 CUSTOMERS", df)


# ============================================================
# 13. CUSTOMER: FEBRUARY vs MARCH
# ============================================================

query = """
SELECT
    customer_id,
    customer_name,

    ROUND(
        SUM(CASE
            WHEN MONTH(order_date) = 2
            THEN sales ELSE 0
        END), 2
    ) AS february_sales,

    ROUND(
        SUM(CASE
            WHEN MONTH(order_date) = 3
            THEN sales ELSE 0
        END), 2
    ) AS march_sales,

    ROUND(
        SUM(CASE
            WHEN MONTH(order_date) = 3
            THEN sales ELSE 0
        END)
        -
        SUM(CASE
            WHEN MONTH(order_date) = 2
            THEN sales ELSE 0
        END),
        2
    ) AS sales_change

FROM orders
WHERE MONTH(order_date) IN (2, 3)
GROUP BY customer_id, customer_name
HAVING sales_change < 0
ORDER BY sales_change ASC
LIMIT 10;
"""

df = get_data(query)
show("CUSTOMERS WITH SALES DECLINE", df)


# ============================================================
# 14. TOP 10 PRODUCTS
# ============================================================

query = """
SELECT
    product_id,
    product_name,
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM orders
GROUP BY product_id, product_name, category
ORDER BY total_sales DESC
LIMIT 10;
"""

df = get_data(query)
show("TOP 10 PRODUCTS", df)


# ============================================================
# 15. HIGH SALES BUT LOW PROFIT PRODUCTS
# ============================================================

query = """
SELECT
    product_name,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM orders
GROUP BY product_name
HAVING SUM(sales) > 1000
ORDER BY total_profit ASC
LIMIT 10;
"""

df = get_data(query)
show("HIGH SALES BUT LOW PROFIT PRODUCTS", df)


# ============================================================
# 16. DISCOUNT vs PROFIT
# ============================================================

query = """
SELECT
    ROUND(discount, 2) AS discount,
    ROUND(AVG(profit), 2) AS average_profit,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM orders
GROUP BY discount
ORDER BY discount;
"""

df = get_data(query)
show("DISCOUNT vs PROFIT", df)


# ============================================================
# 17. SHIPPING MODE ANALYSIS
# ============================================================

query = """
SELECT
    ship_mode,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM orders
GROUP BY ship_mode
ORDER BY total_orders DESC;
"""

df = get_data(query)
show("SHIPPING MODE ANALYSIS", df)


# ============================================================
# 18. DELIVERY TIME ANALYSIS
# ============================================================

query = """
SELECT
    ship_mode,
    ROUND(AVG(DATEDIFF(ship_date, order_date)), 2)
        AS average_delivery_days
FROM orders
GROUP BY ship_mode
ORDER BY average_delivery_days;
"""

df = get_data(query)
show("AVERAGE DELIVERY TIME", df)


# ============================================================
# 19. MAIN BUSINESS QUESTION
# ============================================================

print("\n")
print("=" * 70)
print("MAIN BUSINESS QUESTION")
print("=" * 70)

print("Why did sales drop in March?")

print("\nThe system currently analyzes:")
print("1. Overall sales")
print("2. Monthly sales trend")
print("3. February vs March")
print("4. Category performance")
print("5. Region performance")
print("6. Customer performance")
print("7. Product performance")
print("8. Profit performance")
print("9. Discount impact")
print("10. Shipping performance")


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("STEP 4 ANALYSIS COMPLETE")
print("=" * 70)