import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Please check the .env file in the project root."
    )


# ============================================================
# 2. GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=api_key
)


# ============================================================
# 3. DATABASE SCHEMA
# ============================================================

DATABASE_SCHEMA = """
Database: ai_business_analyst_db

Table: orders

Columns:

row_id INT
order_id VARCHAR
order_date DATE
ship_date DATE
ship_mode VARCHAR
customer_id VARCHAR
customer_name VARCHAR
segment VARCHAR
country VARCHAR
city VARCHAR
state VARCHAR
postal_code INT
region VARCHAR
product_id VARCHAR
category VARCHAR
sub_category VARCHAR
product_name VARCHAR
sales DECIMAL
quantity INT
discount DECIMAL
profit DECIMAL
"""


# ============================================================
# 4. GENERATE SQL
# ============================================================

def generate_sql(question):

    question = question.strip()

    if not question:
        raise ValueError(
            "Business question cannot be empty."
        )


    # ========================================================
    # SPECIAL CASE: TOTAL SALES
    # ========================================================

    question_lower = question.lower()

    if (
        "total sales" in question_lower
        and "category" not in question_lower
        and "region" not in question_lower
        and "customer" not in question_lower
        and "product" not in question_lower
    ):

        return (
            "SELECT SUM(sales) AS total_sales "
            "FROM orders"
        )


    # ========================================================
    # SPECIAL CASE: TOTAL PROFIT
    # ========================================================

    if (
        "total profit" in question_lower
        and "category" not in question_lower
        and "region" not in question_lower
        and "customer" not in question_lower
        and "product" not in question_lower
    ):

        return (
            "SELECT SUM(profit) AS total_profit "
            "FROM orders"
        )


    # ========================================================
    # SPECIAL CASE: TOTAL QUANTITY
    # ========================================================

    if (
        "total quantity" in question_lower
        and "category" not in question_lower
        and "region" not in question_lower
        and "customer" not in question_lower
        and "product" not in question_lower
    ):

        return (
            "SELECT SUM(quantity) AS total_quantity "
            "FROM orders"
        )


    # ========================================================
    # GEMINI SQL GENERATION
    # ========================================================

    prompt = f"""
You are an expert PostgreSQL Business Analyst.

Your task is to convert the user's EXACT natural-language
business question into ONE accurate PostgreSQL SELECT query.

DATABASE SCHEMA
---------------

{DATABASE_SCHEMA}


STRICT SQL RULES
----------------

1. ALWAYS use the `orders` table.

2. Use ONLY columns that exist in the schema.

3. Generate ONLY ONE SELECT statement.

4. NEVER generate:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   CREATE
   TRUNCATE
   RENAME
   GRANT
   REVOKE

5. NEVER modify the database.

6. Return ONLY the SQL query.

7. Do NOT return markdown.

8. Do NOT return ```sql.

9. Do NOT explain the SQL query.

10. Use valid PostgreSQL syntax.

11. For aggregation questions, use:
    SUM()
    AVG()
    COUNT()
    MIN()
    MAX()

12. For grouped analysis, use GROUP BY.

13. For highest/lowest questions, use ORDER BY and LIMIT.

14. For highest SALES questions:
    ALWAYS return both the requested dimension and
    the sales amount.

15. For lowest SALES questions:
    ALWAYS return both the requested dimension and
    the sales amount.

16. For highest PROFIT questions:
    ALWAYS return both the requested dimension and
    the profit amount.

17. For lowest PROFIT questions:
    ALWAYS return both the requested dimension and
    the profit amount.

18. NEVER return only a category, region, customer,
    or product when the user asks about sales or profit.

19. For sales analysis, use the `sales` column.

20. For profit analysis, use the `profit` column.

21. For quantity analysis, use the `quantity` column.

22. For discount analysis, use the `discount` column.

23. For customer analysis, use customer_id and/or customer_name.

24. For product analysis, use product_id and/or product_name.

25. For category analysis, use category.

26. For sub-category analysis, use sub_category.

27. For region analysis, use region.

28. For segment analysis, use segment.

29. For monthly analysis, use PostgreSQL syntax:

    EXTRACT(YEAR FROM order_date)
    EXTRACT(MONTH FROM order_date)

30. If the user specifies a year, filter ONLY that year.

31. If the user specifies a month and year, filter ONLY
    that month and year.

32. If the user specifies a category, preserve that constraint.

33. If the user specifies a region, preserve that constraint.

34. If the user specifies a customer, preserve that constraint.

35. If the user specifies a product, preserve that constraint.

36. If the user asks for a comparison, compare ONLY the
    requested periods, categories, regions, customers,
    or products.

37. Do NOT add unnecessary columns.

38. Do NOT add unnecessary calculations.

39. Do NOT broaden the question.

40. Do NOT silently change the user's question.

41. Answer ONLY the user's exact question.

42. Never answer a different or broader business question.

43. If the user asks for ONE metric, return that metric.

44. If the user asks for a ranking, return the requested ranking.

45. If the user asks for a specific time period, use ONLY
    that time period.

46. If the user asks "why", use measurable factors available
    in the database.

47. For "why" questions, investigate relevant dimensions such as:
    category
    sub_category
    region
    customer
    product
    quantity
    discount
    profit

48. Do NOT claim causation unless the available data supports it.

49. Do NOT invent columns.

50. Do NOT invent business facts.

51. If the question cannot be answered exactly from the schema,
    use the closest valid query using available fields.

52. The final output MUST be one executable SELECT query.

53. NEVER generate multiple SQL statements.

54. NEVER put two SELECT statements in the response.

55. NEVER include an explanation before or after the SQL.

56. Do NOT add a semicolon at the end of the query.

57. Use PostgreSQL-compatible functions and syntax only.

58. Do NOT use MySQL-specific functions such as:
    YEAR()
    MONTH()
    DATE_FORMAT()
    IFNULL()

59. For year extraction use:
    EXTRACT(YEAR FROM order_date)

60. For month extraction use:
    EXTRACT(MONTH FROM order_date)

IMPORTANT EXAMPLES
------------------

Question:
Which category generated the highest sales?

SQL:
SELECT
    category,
    SUM(sales) AS total_sales
FROM orders
GROUP BY category
ORDER BY total_sales DESC
LIMIT 1


Question:
Which region generated the highest profit?

SQL:
SELECT
    region,
    SUM(profit) AS total_profit
FROM orders
GROUP BY region
ORDER BY total_profit DESC
LIMIT 1


Question:
Who are the top 10 customers by sales?

SQL:
SELECT
    customer_id,
    customer_name,
    SUM(sales) AS total_sales
FROM orders
GROUP BY customer_id, customer_name
ORDER BY total_sales DESC
LIMIT 10


Question:
What is the total sales?

SQL:
SELECT
    SUM(sales) AS total_sales
FROM orders


Question:
What is the total quantity?

SQL:
SELECT
    SUM(quantity) AS total_quantity
FROM orders


Question:
What is the total profit?

SQL:
SELECT
    SUM(profit) AS total_profit
FROM orders


Question:
What were the sales in March 2017?

SQL:
SELECT
    SUM(sales) AS total_sales
FROM orders
WHERE EXTRACT(YEAR FROM order_date) = 2017
AND EXTRACT(MONTH FROM order_date) = 3


Question:
Why did sales change in March 2017?

The query should focus ONLY on March 2017
and the relevant comparison period.

Do not answer an unrelated question.


USER QUESTION
-------------

{question}
"""


    # ========================================================
    # CALL GEMINI
    # ========================================================

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

    except Exception as error:

        raise RuntimeError(
            f"Gemini API error: {error}"
        )


    # ========================================================
    # GET GENERATED SQL
    # ========================================================

    sql = response.text.strip()


    # ========================================================
    # REMOVE MARKDOWN CODE FENCES
    # ========================================================

    sql = sql.replace("```postgresql", "")
    sql = sql.replace("```PostgreSQL", "")
    sql = sql.replace("```sql", "")
    sql = sql.replace("```SQL", "")
    sql = sql.replace("```", "")

    sql = sql.strip()


    # ========================================================
    # REMOVE TRAILING SEMICOLON
    # ========================================================

    sql = sql.rstrip(";").strip()


    # ========================================================
    # ENSURE ONLY ONE SQL STATEMENT
    # ========================================================

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    if len(statements) > 1:

        raise ValueError(
            "AI generated multiple SQL statements. "
            "Only one SELECT statement is allowed."
        )


    # ========================================================
    # BASIC SELECT CHECK
    # ========================================================

    if not sql.upper().startswith("SELECT"):

        raise ValueError(
            "AI did not generate a valid SELECT query."
        )


    return sql


# ============================================================
# 5. SQL VALIDATION
# ============================================================

def validate_sql(sql):

    if not sql:

        return False, "Query is empty."


    sql_clean = sql.strip()

    sql_upper = sql_clean.upper()


    # --------------------------------------------------------
    # Must start with SELECT
    # --------------------------------------------------------

    if not sql_upper.startswith("SELECT"):

        return False, (
            "Query must start with SELECT."
        )


    # --------------------------------------------------------
    # Block dangerous SQL commands
    # --------------------------------------------------------

    forbidden_commands = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "RENAME",
        "GRANT",
        "REVOKE"
    ]


    for command in forbidden_commands:

        pattern = r"\b" + command + r"\b"

        if re.search(
            pattern,
            sql_upper
        ):

            return False, (
                f"Forbidden SQL command detected: {command}"
            )


    # --------------------------------------------------------
    # Must use orders table
    # --------------------------------------------------------

    orders_pattern = (
        r"\bFROM\s+"
        r"(?:"
        r"`?AI_BUSINESS_ANALYST_DB`?"
        r"\s*\.\s*"
        r")?"
        r"`?ORDERS`?"
        r"(?:\s|$)"
    )


    if not re.search(
        orders_pattern,
        sql_upper
    ):

        return False, (
            "Query must use the orders table."
        )


    # --------------------------------------------------------
    # Block multiple SQL statements
    # --------------------------------------------------------

    statements = [
        statement.strip()
        for statement in sql_clean.split(";")
        if statement.strip()
    ]


    if len(statements) > 1:

        return False, (
            "Multiple SQL statements are not allowed."
        )


    # --------------------------------------------------------
    # Block SQL comments
    # --------------------------------------------------------

    if "--" in sql_clean:

        return False, (
            "SQL comments are not allowed."
        )


    if "/*" in sql_clean or "*/" in sql_clean:

        return False, (
            "SQL block comments are not allowed."
        )


    # --------------------------------------------------------
    # Block unsafe SQL patterns
    # --------------------------------------------------------

    dangerous_patterns = [
        r"\bINTO\s+OUTFILE\b",
        r"\bINTO\s+DUMPFILE\b",
        r"\bLOAD_FILE\s*\(",
        r"\bSLEEP\s*\(",
        r"\bBENCHMARK\s*\("
    ]


    for pattern in dangerous_patterns:

        if re.search(
            pattern,
            sql_upper
        ):

            return False, (
                "Unsafe SQL pattern detected."
            )


    # --------------------------------------------------------
    # Block MySQL-specific syntax
    # --------------------------------------------------------

    mysql_patterns = [
        r"\bYEAR\s*\(",
        r"\bMONTH\s*\(",
        r"\bDATE_FORMAT\s*\(",
        r"\bIFNULL\s*\("
    ]


    for pattern in mysql_patterns:

        if re.search(
            pattern,
            sql_upper
        ):

            return False, (
                "MySQL-specific syntax detected. "
                "Use PostgreSQL syntax instead."
            )


    # --------------------------------------------------------
    # Validation successful
    # --------------------------------------------------------

    return True, "SQL validation passed."


# ============================================================
# 6. TEST PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AI BUSINESS ANALYST - POSTGRESQL TEXT TO SQL")
    print("=" * 70)


    question = input(
        "\nEnter your business question: "
    ).strip()


    if not question:

        print(
            "\nNo question entered."
        )

        exit()


    print(
        "\nGenerating SQL..."
    )


    try:

        sql = generate_sql(
            question
        )

    except Exception as error:

        print(
            "\nERROR:"
        )

        print(error)

        exit()


    print(
        "\n" + "=" * 70
    )

    print(
        "GENERATED SQL"
    )

    print(
        "=" * 70
    )

    print(sql)


    valid, message = validate_sql(
        sql
    )


    print(
        "\n" + "=" * 70
    )

    print(
        "SQL VALIDATION"
    )

    print(
        "=" * 70
    )


    if valid:

        print(
            "PASSED"
        )

        print(
            message
        )

    else:

        print(
            "FAILED"
        )

        print(
            "Reason:",
            message
        )