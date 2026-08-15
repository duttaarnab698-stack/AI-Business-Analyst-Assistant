from flask import Flask, request, jsonify
from flask_cors import CORS

from ai_analyst import process_question


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# CORS
# Allow Vercel frontend to call Render API
# ============================================================

CORS(
    app,
    resources={
        r"/*": {
            "origins": "*"
        }
    },
    methods=[
        "GET",
        "POST",
        "OPTIONS"
    ],
    allow_headers=[
        "Content-Type",
        "Authorization"
    ]
)


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "running",
        "message": "AI Business Analyst API is running"
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "AI Business Analyst API"
    })


# ============================================================
# ASK QUESTION
# ============================================================

@app.route("/ask", methods=["POST", "OPTIONS"])
def ask_question():

    # --------------------------------------------------------
    # Browser CORS preflight request
    # --------------------------------------------------------

    if request.method == "OPTIONS":

        return jsonify({
            "success": True
        }), 200


    try:

        # ----------------------------------------------------
        # Read JSON
        # ----------------------------------------------------

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({
                "success": False,
                "error": "Request body must contain JSON."
            }), 400


        # ----------------------------------------------------
        # Get question
        # ----------------------------------------------------

        question = data.get(
            "question"
        )


        if question is None:

            return jsonify({
                "success": False,
                "error": "Question is required."
            }), 400


        question = str(
            question
        ).strip()


        if not question:

            return jsonify({
                "success": False,
                "error": "Question cannot be empty."
            }), 400


        # ----------------------------------------------------
        # Process AI business question
        # ----------------------------------------------------

        result = process_question(
            question
        )


        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return jsonify(
            result
        ), 200


    except Exception as error:

        print(
            "\nAPI ERROR:"
        )

        print(
            error
        )


        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )