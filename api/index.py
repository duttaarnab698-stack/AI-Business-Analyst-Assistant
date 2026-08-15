"""Vercel entry point for the AI Business Analyst Flask API."""
from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.ai_analyst import process_question


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])


def public_error(message):
    """Keep provider/database internals out of browser responses."""
    message, lowered = str(message), str(message).lower()
    if "429" in lowered or "resource_exhausted" in lowered:
        return "The AI service is busy. Please wait a moment and try again."
    if any(code in lowered for code in ("401", "403")):
        return "The AI service configuration is unavailable. Please try again later."
    if any(token in lowered for token in ("500", "502", "503", "timeout", "connection", "gemini", "database error", "psycopg")):
        return "The analysis service is temporarily unavailable. Please try again shortly."
    return message if len(message) <= 300 else "Unable to analyze this question. Please try again."


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
            result["error"] = public_error(result.get("error", "Unable to analyze this question."))
        return jsonify(result), 200 if result.get("success") else 422
    except Exception:
        app.logger.exception("Question processing failed")
        return jsonify({
            "success": False,
            "error": "The analysis service is temporarily unavailable. Please try again shortly.",
        }), 503
