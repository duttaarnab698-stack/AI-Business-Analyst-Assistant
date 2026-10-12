"""Vercel entry point for the AI Business Analyst Flask API."""
import re

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.ai_analyst import process_question
from backend.database import dispose_engine


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])


@app.teardown_appcontext
def close_serverless_database_connections(exception=None):
    """Do not retain idle PostgreSQL sockets in a warm Vercel function."""
    dispose_engine()


def error_stage(message):
    """Classify an existing backend failure without changing its source."""
    lowered = str(message).lower()
    if "sql generation" in lowered or "sql validation" in lowered:
        return "sql_generation"
    if "database" in lowered or "psycopg" in lowered or "sqlalchemy" in lowered:
        return "database"
    if "gemini" in lowered or "resource_exhausted" in lowered or any(code in lowered for code in ("429", "401", "403")):
        return "gemini"
    return "unknown"


def safe_error(message):
    """Expose debugging context while redacting credentials and connection URLs."""
    message = str(message)
    message = re.sub(r"postgres(?:ql)?(?:\+[^:]+)?://[^\s'\"]+", "[REDACTED_DATABASE_URL]", message)
    message = re.sub(r"AIza[\w-]+", "[REDACTED_GEMINI_API_KEY]", message)
    message = re.sub(r"(?i)(gemini_api_key|database_url)\s*[=:]\s*[^\s,]+", r"\1=[REDACTED]", message)
    if "429" in message or "RESOURCE_EXHAUSTED" in message.upper():
        return "Gemini API quota/rate limit exceeded. " + message[:500]
    return message[:700]


@app.get("/")
@app.get("/api")
@app.get("/api/")
def home():
    return jsonify({
        "status": "running",
        "message": "AI Business Analyst API is running on Vercel",
    })


@app.get("/health")
@app.get("/api/health")
def health():
    return jsonify({"success": True, "status": "healthy"})


@app.route("/ask", methods=["POST", "OPTIONS"])
@app.route("/api/ask", methods=["POST", "OPTIONS"])
def ask_question():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Request body must contain valid JSON."}), 400

    question = data.get("question")
    if not isinstance(question, str) or not question.strip():
        return jsonify({"success": False, "error": "Question cannot be empty."}), 400

    try:
        result = process_question(question.strip())
        if not result.get("success"):
            actual_error = result.get("error", "Unable to analyze this question.")
            stage = error_stage(actual_error)
            app.logger.error("Question processing failed at %s: %s", stage, actual_error)
            return jsonify({
                "success": False,
                "error": safe_error(actual_error),
                "stage": stage,
            }), 422
        return jsonify(result), 200 if result.get("success") else 422
    except Exception as error:
        app.logger.exception("Question processing failed")
        return jsonify({
            "success": False,
            "error": safe_error(error),
            "stage": error_stage(error),
        }), 503
