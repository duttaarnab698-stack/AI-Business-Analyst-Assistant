"""Rule-based analytics for the PostgreSQL ``orders`` table.

This module intentionally has no model client or external API dependency.  A
question is matched to a small, fixed catalog of read-only SQL statements.
"""

import json
import re

from .database import get_data


UNSUPPORTED_MESSAGE = (
    "I can answer questions about sales, profit, quantity, orders, products, "
    "categories, regions, segments, and averages."
)

METRICS = {
    "sales": {"column": "sales", "label": "sales", "currency": True},
    "profit": {"column": "profit", "label": "profit", "currency": True},
    "quantity": {"column": "quantity", "label": "quantity", "currency": False},
}

DIMENSIONS = {
    "category": {"column": "category", "label": "category", "terms": ("category", "categories")},
    "region": {"column": "region", "label": "region", "terms": ("region", "regions")},
    "product": {"column": "product_name", "label": "product", "terms": ("product", "products")},
    "segment": {"column": "segment", "label": "segment", "terms": ("segment", "segments")},
}

HIGHEST_WORDS = ("highest", "top", "most", "best", "largest", "maximum")


def _normalized(question):
    return re.sub(r"\s+", " ", question.lower()).strip()


def _metric_for(question):
    if "profit" in question or "profits" in question:
        return "profit"
    if "quantity" in question or "units" in question:
        return "quantity"
    if "sales" in question or "revenue" in question:
        return "sales"
    return None


def _dimension_for(question):
    for name, config in DIMENSIONS.items():
        if any(term in question for term in config["terms"]):
            return name
    return None


def _format_value(value, metric):
    if value is None:
        return "0"
    if metric and METRICS[metric]["currency"]:
        return f"${float(value):,.2f}"
    if metric == "quantity":
        return f"{float(value):,.0f}"
    return f"{float(value):,.2f}"


def _rows_as_json(df):
    """Convert pandas/psycopg values to JSON-native values for Flask."""
    return json.loads(df.to_json(orient="records"))


def _unsupported(question):
    return {
        "success": False,
        "question": question,
        "error": UNSUPPORTED_MESSAGE,
        "sql": None,
        "answer": UNSUPPORTED_MESSAGE,
        "data": [],
    }


def _run(question, sql, answer_builder):
    try:
        df = get_data(sql)
    except Exception as error:
        return {
            "success": False,
            "question": question,
            "error": f"Database Error: {error}",
            "sql": sql,
            "answer": "The database query could not be completed.",
            "data": [],
        }

    rows = _rows_as_json(df)
    return {
        "success": True,
        "question": question,
        "sql": sql,
        "answer": answer_builder(rows),
        "data": rows,
    }


def _total_question(question, metric):
    config = METRICS[metric]
    sql = (
        f"SELECT ROUND(SUM({config['column']}), 2) AS total_{metric} "
        "FROM orders"
    )

    def answer(rows):
        value = rows[0].get(f"total_{metric}") if rows else None
        verb = "are" if metric == "sales" else "is"
        return f"Total {config['label']} {verb} {_format_value(value, metric)}."

    return _run(question, sql, answer)


def _average_sales(question):
    sql = "SELECT ROUND(AVG(sales), 2) AS average_sales FROM orders"

    def answer(rows):
        value = rows[0].get("average_sales") if rows else None
        return f"Average sales are {_format_value(value, 'sales')}."

    return _run(question, sql, answer)


def _order_count(question):
    sql = "SELECT COUNT(DISTINCT order_id) AS total_orders FROM orders"

    def answer(rows):
        value = rows[0].get("total_orders", 0) if rows else 0
        return f"There are {int(value):,} orders."

    return _run(question, sql, answer)


def _grouped_question(question, metric, dimension, highest):
    metric_config = METRICS[metric]
    dimension_config = DIMENSIONS[dimension]
    column = dimension_config["column"]
    alias = f"total_{metric}"
    sql = (
        f"SELECT {column}, ROUND(SUM({metric_config['column']}), 2) AS {alias} "
        f"FROM orders GROUP BY {column} ORDER BY {alias} DESC"
    )
    if highest:
        sql += " LIMIT 1"

    def answer(rows):
        if not rows:
            return "No matching data was found."
        if highest:
            row = rows[0]
            value = _format_value(row.get(alias), metric)
            return (
                f"The {dimension_config['label']} with the highest "
                f"{metric_config['label']} is {row.get(column)} at {value}."
            )
        summary = "; ".join(
            f"{row.get(column)}: {_format_value(row.get(alias), metric)}"
            for row in rows
        )
        return f"{metric_config['label'].title()} by {dimension_config['label']}: {summary}."

    return _run(question, sql, answer)


def process_question(question):
    """Match a supported question to one predefined, read-only query."""
    question = question.strip()
    if not question:
        return _unsupported(question)

    normalized = _normalized(question)
    if "order" in normalized and any(
        phrase in normalized
        for phrase in ("how many", "number of", "count", "total orders")
    ):
        return _order_count(question)

    if "average" in normalized or "avg" in normalized:
        if _metric_for(normalized) == "sales":
            return _average_sales(question)
        return _unsupported(question)

    metric = _metric_for(normalized)
    dimension = _dimension_for(normalized)
    highest = any(word in normalized for word in HIGHEST_WORDS)

    if metric and dimension:
        return _grouped_question(question, metric, dimension, highest)
    if metric and not dimension and (
        "total" in normalized or "how much" in normalized or "what is" in normalized
    ):
        return _total_question(question, metric)

    return _unsupported(question)
