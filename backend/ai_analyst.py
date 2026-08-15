import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# IMPORTANT:
# ai_analyst.py এবং sql_generator.py/database.py
# একই backend folder-এর মধ্যে আছে।
from .sql_generator import generate_sql, validate_sql
from .database import get_data


# ============================================================
# 1. LOAD ENVIRONMENT
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
# 3. CHECK ROOT-CAUSE QUESTION
# ============================================================

def is_why_question(question):

    question_lower = question.lower().strip()

    why_patterns = [
        "why",
        "reason",
        "cause",
        "caused",
        "decline",
        "decreased",
        "dropped",
        "drop",
        "fall",
        "fell"
    ]

    return any(
        pattern in question_lower
        for pattern in why_patterns
    )


# ============================================================
# 4. EXTRACT YEAR AND MONTH
# ============================================================

def extract_period(question):

    question_lower = question.lower()

    year = None
    month = None

    year_match = re.search(
        r"\b(20\d{2})\b",
        question_lower
    )

    if year_match:
        year = int(year_match.group(1))

    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12
    }

    for month_name, month_number in months.items():

        if month_name in question_lower:

            month = month_number

            break

    return year, month


# ============================================================
# 5. GET PREVIOUS MONTH
# ============================================================

def get_previous_month(year, month):

    if month == 1:

        return year - 1, 12

    return year, month - 1


# ============================================================
# 6. ROOT CAUSE ANALYSIS
# ============================================================

def root_cause_analysis(question):

    year, month = extract_period(question)

    if year is None or month is None:

        return {
            "success": False,
            "error": (
                "For root-cause analysis, please specify "
                "both month and year. Example: "
                "'Why did sales change in March 2017?'"
            )
        }


    previous_year, previous_month = get_previous_month(
        year,
        month
    )


    # ========================================================
    # 1. OVERALL PERFORMANCE
    # ========================================================

    query = f"""
    SELECT
        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS previous_sales,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS current_sales,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN profit
                    ELSE 0
                END
            ),
            2
        ) AS previous_profit,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN profit
                    ELSE 0
                END
            ),
            2
        ) AS current_profit,

        SUM(
            CASE
                WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                AND EXTRACT(MONTH FROM order_date) = {previous_month}
                THEN quantity
                ELSE 0
            END
        ) AS previous_quantity,

        SUM(
            CASE
                WHEN EXTRACT(YEAR FROM order_date) = {year}
                AND EXTRACT(MONTH FROM order_date) = {month}
                THEN quantity
                ELSE 0
            END
        ) AS current_quantity

    FROM orders
    """

    overall = get_data(query)


    # ========================================================
    # 2. CATEGORY ANALYSIS
    # ========================================================

    query = f"""
    SELECT
        category,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS previous_sales,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS current_sales,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            )
            -
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS sales_change

    FROM orders

    WHERE
        (
            EXTRACT(YEAR FROM order_date) = {previous_year}
            AND EXTRACT(MONTH FROM order_date) = {previous_month}
        )
        OR
        (
            EXTRACT(YEAR FROM order_date) = {year}
            AND EXTRACT(MONTH FROM order_date) = {month}
        )

    GROUP BY category

    ORDER BY sales_change ASC
    """

    category = get_data(query)


    # ========================================================
    # 3. REGION ANALYSIS
    # ========================================================

    query = f"""
    SELECT
        region,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS previous_sales,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS current_sales,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            )
            -
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS sales_change

    FROM orders

    WHERE
        (
            EXTRACT(YEAR FROM order_date) = {previous_year}
            AND EXTRACT(MONTH FROM order_date) = {previous_month}
        )
        OR
        (
            EXTRACT(YEAR FROM order_date) = {year}
            AND EXTRACT(MONTH FROM order_date) = {month}
        )

    GROUP BY region

    ORDER BY sales_change ASC
    """

    region = get_data(query)


    # ========================================================
    # 4. CUSTOMER ANALYSIS
    # ========================================================

    query = f"""
    SELECT
        customer_id,
        customer_name,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS previous_sales,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS current_sales,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            )
            -
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS sales_change

    FROM orders

    WHERE
        (
            EXTRACT(YEAR FROM order_date) = {previous_year}
            AND EXTRACT(MONTH FROM order_date) = {previous_month}
        )
        OR
        (
            EXTRACT(YEAR FROM order_date) = {year}
            AND EXTRACT(MONTH FROM order_date) = {month}
        )

    GROUP BY customer_id, customer_name

    HAVING
        (
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            )
            -
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            )
        ) < 0

    ORDER BY sales_change ASC

    LIMIT 10
    """

    customer = get_data(query)


    # ========================================================
    # 5. PRODUCT ANALYSIS
    # ========================================================

    query = f"""
    SELECT
        product_id,
        product_name,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS previous_sales,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS current_sales,

        ROUND(
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            )
            -
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            ),
            2
        ) AS sales_change

    FROM orders

    WHERE
        (
            EXTRACT(YEAR FROM order_date) = {previous_year}
            AND EXTRACT(MONTH FROM order_date) = {previous_month}
        )
        OR
        (
            EXTRACT(YEAR FROM order_date) = {year}
            AND EXTRACT(MONTH FROM order_date) = {month}
        )

    GROUP BY product_id, product_name

    HAVING
        (
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN sales
                    ELSE 0
                END
            )
            -
            SUM(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN sales
                    ELSE 0
                END
            )
        ) < 0

    ORDER BY sales_change ASC

    LIMIT 10
    """

    product = get_data(query)


    # ========================================================
    # 6. DISCOUNT + PROFIT ANALYSIS
    # ========================================================

    query = f"""
    SELECT
        ROUND(
            AVG(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN discount
                END
            ),
            4
        ) AS previous_avg_discount,

        ROUND(
            AVG(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN discount
                END
            ),
            4
        ) AS current_avg_discount,

        ROUND(
            AVG(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {previous_year}
                    AND EXTRACT(MONTH FROM order_date) = {previous_month}
                    THEN profit
                END
            ),
            2
        ) AS previous_avg_profit,

        ROUND(
            AVG(
                CASE
                    WHEN EXTRACT(YEAR FROM order_date) = {year}
                    AND EXTRACT(MONTH FROM order_date) = {month}
                    THEN profit
                END
            ),
            2
        ) AS current_avg_profit

    FROM orders
    """

    discount = get_data(query)


    return {
        "success": True,
        "year": year,
        "month": month,
        "previous_year": previous_year,
        "previous_month": previous_month,
        "overall": overall,
        "category": category,
        "region": region,
        "customer": customer,
        "product": product,
        "discount": discount
    }


# ============================================================
# 7. GENERATE ROOT-CAUSE AI INSIGHT
# ============================================================

def generate_root_cause_insight(question, analysis):

    year = analysis["year"]
    month = analysis["month"]

    previous_year = analysis["previous_year"]
    previous_month = analysis["previous_month"]

    overall_text = analysis["overall"].to_string(
        index=False
    )

    category_text = analysis["category"].to_string(
        index=False
    )

    region_text = analysis["region"].to_string(
        index=False
    )

    customer_text = analysis["customer"].to_string(
        index=False
    )

    product_text = analysis["product"].to_string(
        index=False
    )

    discount_text = analysis["discount"].to_string(
        index=False
    )


    prompt = f"""
You are a senior AI Business Analyst.

You must answer ONLY the user's exact question.

USER QUESTION:
{question}

CURRENT PERIOD:
{month}/{year}

PREVIOUS PERIOD:
{previous_month}/{previous_year}

OVERALL PERFORMANCE:
{overall_text}

CATEGORY ANALYSIS:
{category_text}

REGION ANALYSIS:
{region_text}

CUSTOMER ANALYSIS:
{customer_text}

PRODUCT ANALYSIS:
{product_text}

DISCOUNT AND PROFIT ANALYSIS:
{discount_text}


STRICT RULES:

1. Answer ONLY the exact question asked.

2. Do NOT answer a different or broader question.

3. Use ONLY the supplied database results.

4. Never invent facts, numbers, customers, products, or causes.

5. Verify whether the user's assumption is actually correct.

6. If the user says sales dropped but the data shows
   sales increased, explicitly correct the assumption.

7. If the user says sales increased but the data shows
   sales dropped, explicitly correct the assumption.

8. Analyze ONLY the requested time period.

9. Do not discuss unrelated months or years.

10. If the question asks WHY, identify evidence-based
    contributing factors.

11. Do not claim causation unless the data supports it.

12. Clearly distinguish between:
    - observed result
    - contributing factor
    - proven cause

13. Do not add unrelated recommendations.

14. If the data is insufficient to determine a cause,
    say so.

15. Keep the answer concise and business-focused.


RETURN FORMAT:

Business Summary:
<direct answer to the exact question>

Sales Change:
<only if relevant to the question>

Top Root Causes:
1. <most relevant factor>
2. <second relevant factor>
3. <third relevant factor>

Supporting Evidence:
- <relevant number>
- <relevant number>
- <relevant number>

Business Recommendation:
<only if relevant to the user's question>
"""


    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as error:

        raise RuntimeError(
            f"Gemini Insight Error: {error}"
        )


# ============================================================
# 8. NORMAL BUSINESS QUESTION
# ============================================================

def normal_business_question(question):

    print("\nGenerating SQL...")


    # ========================================================
    # GENERATE SQL
    # ========================================================

    try:

        sql = generate_sql(
            question
        )

    except Exception as error:

        print("\nSQL Generation Error:")
        print(error)

        return {
            "success": False,
            "error": f"SQL Generation Error: {error}"
        }


    print("\n" + "=" * 70)
    print("GENERATED SQL")
    print("=" * 70)

    print(sql)


    # ========================================================
    # SQL VALIDATION
    # ========================================================

    valid, message = validate_sql(
        sql
    )

    print("\n" + "=" * 70)
    print("SQL VALIDATION")
    print("=" * 70)


    if not valid:

        print("FAILED")
        print("Reason:", message)

        return {
            "success": False,
            "error": f"SQL Validation Failed: {message}",
            "sql": sql
        }


    print("PASSED")


    # ========================================================
    # DATABASE EXECUTION
    # ========================================================

    try:

        df = get_data(
            sql
        )

    except Exception as error:

        print("\nDatabase Error:")
        print(error)

        return {
            "success": False,
            "error": f"Database Error: {error}",
            "sql": sql
        }


    print("\n" + "=" * 70)
    print("DATABASE RESULT")
    print("=" * 70)


    if df.empty:

        print("No data found.")

        return {
            "success": True,
            "question": question,
            "sql": sql,
            "answer": "No data was found for this question.",
            "data": []
        }


    print(
        df.to_string(
            index=False
        )
    )


    # ========================================================
    # DATABASE RESULT → TEXT
    # ========================================================

    result_text = df.to_string(
        index=False
    )


    # ========================================================
    # GEMINI BUSINESS ANSWER
    # ========================================================

    prompt = f"""
You are an AI Business Analyst.

Answer ONLY the user's exact business question.

USER QUESTION:
{question}

DATABASE RESULT:
{result_text}


IMPORTANT RULES:

1. The DATABASE RESULT is the source of truth.

2. A result containing only ONE ROW is NOT automatically
   insufficient.

3. If the SQL query uses ORDER BY ... DESC LIMIT 1,
   the returned row represents the highest/top result.

4. If the SQL query uses ORDER BY ... ASC LIMIT 1,
   the returned row represents the lowest/bottom result.

5. If the question asks which category generated the
   highest sales and the database returns:

   category | total_sales
   Technology | 836154.1

   then directly answer:

   Technology generated the highest sales,
   with total sales of $836,154.10.

6. If the question asks which region generated the
   highest profit and the database returns one row
   produced by ORDER BY profit DESC LIMIT 1,
   directly answer that region and profit value.

7. If the question asks for a total and the database
   returns one total row, directly give that total.

8. If the question asks for a ranking, use the returned
   ranking rows.

9. If the question asks for a comparison, compare only
   the requested values.

10. If the user's assumption is incorrect, correct it
    using the database result.

11. Do NOT invent facts, numbers, categories, regions,
    customers, products, or explanations.

12. Do NOT say "the available data is insufficient"
    merely because the database returned one row.

13. Say "The available data is insufficient to answer
    this question" ONLY when the database result genuinely
    does not contain enough information to answer the
    exact question.

14. Answer ONLY the exact question.

15. Do NOT add unrelated recommendations.

16. Do NOT add unrelated analysis.

17. Keep the answer concise and business-focused.

18. Preserve all user constraints:
    - month
    - year
    - category
    - region
    - customer
    - product
    - metric
    - ranking
    - comparison


RETURN FORMAT:

Business Insight:
<direct answer to the exact question>

Key Finding:
<one concise supporting finding>
"""


    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        answer = response.text.strip()


    except Exception as error:

        print("\nGemini Insight Error:")
        print(error)

        return {
            "success": False,
            "error": f"Gemini Insight Error: {error}",
            "sql": sql,
            "data": df.to_dict(
                orient="records"
            )
        }


    # ========================================================
    # SAFETY FALLBACK
    # ========================================================

    if (
        len(df) == 1
        and "insufficient" in answer.lower()
    ):

        row = df.iloc[0]

        columns = list(
            df.columns
        )

        entity_columns = [
            "category",
            "region",
            "sub_category",
            "customer_name",
            "product_name",
            "product_id",
            "customer_id",
            "segment",
            "ship_mode"
        ]

        value_columns = [
            "total_sales",
            "total_profit",
            "sales",
            "profit",
            "total_quantity",
            "quantity",
            "count",
            "total_orders",
            "total_customers"
        ]

        entity_column = None
        value_column = None


        for column in entity_columns:

            if column in columns:

                entity_column = column

                break


        for column in value_columns:

            if column in columns:

                value_column = column

                break


        if entity_column and value_column:

            entity = row[
                entity_column
            ]

            value = row[
                value_column
            ]


            try:

                if isinstance(
                    value,
                    float
                ):

                    formatted_value = (
                        f"{value:,.2f}"
                    )

                else:

                    formatted_value = (
                        f"{value:,}"
                    )

            except Exception:

                formatted_value = str(
                    value
                )


            readable_value_name = (
                value_column
                .replace(
                    "_",
                    " "
                )
            )


            answer = (
                "Business Insight:\n"
                f"{entity} is the answer to your question, "
                f"with {readable_value_name} of "
                f"{formatted_value}.\n\n"
                "Key Finding:\n"
                f"{entity} has the highest result returned "
                f"by the database query."
            )


    print("\n" + "=" * 70)
    print("AI BUSINESS INSIGHT")
    print("=" * 70)

    print(answer)


    # ========================================================
    # RETURN RESULT TO API
    # ========================================================

    return {
        "success": True,
        "question": question,
        "sql": sql,
        "answer": answer,
        "data": df.to_dict(
            orient="records"
        )
    }


# ============================================================
# 9. PROCESS ANY BUSINESS QUESTION
# ============================================================

def process_question(question):

    question = question.strip()


    if not question:

        return {
            "success": False,
            "error": "Please enter a business question."
        }


    # ========================================================
    # ROOT CAUSE QUESTION
    # ========================================================

    if is_why_question(question):

        print(
            "\nRoot-cause question detected."
        )


        analysis = root_cause_analysis(
            question
        )


        if not analysis.get(
            "success",
            False
        ):

            return analysis


        print(
            "\n" + "=" * 70
        )

        print(
            "ROOT CAUSE ANALYSIS DATA"
        )

        print(
            "=" * 70
        )


        print("\nOVERALL:")

        print(
            analysis["overall"].to_string(
                index=False
            )
        )


        print("\nCATEGORY:")

        print(
            analysis["category"].to_string(
                index=False
            )
        )


        print("\nREGION:")

        print(
            analysis["region"].to_string(
                index=False
            )
        )


        print("\nCUSTOMERS:")

        print(
            analysis["customer"].to_string(
                index=False
            )
        )


        print("\nPRODUCTS:")

        print(
            analysis["product"].to_string(
                index=False
            )
        )


        print("\nDISCOUNT:")

        print(
            analysis["discount"].to_string(
                index=False
            )
        )


        print(
            "\n" + "=" * 70
        )

        print(
            "AI ROOT CAUSE INSIGHT"
        )

        print(
            "=" * 70
        )


        try:

            insight = generate_root_cause_insight(
                question,
                analysis
            )

            print(
                insight
            )


            return {
                "success": True,
                "question": question,
                "answer": insight,
                "type": "root_cause",
                "analysis": {
                    "overall": analysis[
                        "overall"
                    ].to_dict(
                        orient="records"
                    ),

                    "category": analysis[
                        "category"
                    ].to_dict(
                        orient="records"
                    ),

                    "region": analysis[
                        "region"
                    ].to_dict(
                        orient="records"
                    ),

                    "customer": analysis[
                        "customer"
                    ].to_dict(
                        orient="records"
                    ),

                    "product": analysis[
                        "product"
                    ].to_dict(
                        orient="records"
                    ),

                    "discount": analysis[
                        "discount"
                    ].to_dict(
                        orient="records"
                    )
                }
            }


        except Exception as error:

            print(
                "\nGemini Error:"
            )

            print(
                error
            )


            return {
                "success": False,
                "error": f"Gemini Error: {error}"
            }


    # ========================================================
    # NORMAL BUSINESS QUESTION
    # ========================================================

    return normal_business_question(
        question
    )


# ============================================================
# 10. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AI BUSINESS ANALYST ASSISTANT")
    print("=" * 70)


    question = input(
        "\nEnter your business question: "
    ).strip()


    result = process_question(
        question
    )


    # ========================================================
    # FINAL STATUS
    # ========================================================

    if not result.get(
        "success",
        False
    ):

        print(
            "\nERROR:"
        )

        print(
            result.get(
                "error",
                "Unknown error."
            )
        )