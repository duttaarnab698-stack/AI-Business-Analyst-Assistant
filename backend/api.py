from flask import Flask, request, jsonify
from flask_cors import CORS

from ai_analyst import process_question


app = Flask(__name__)

CORS(app)


@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "running",
        "message": "AI Business Analyst API is running"
    })


@app.route("/ask", methods=["POST"])
def ask_question():

    try:

        data = request.get_json()

        if not data or "question" not in data:

            return jsonify({
                "success": False,
                "error": "Question is required."
            }), 400


        question = data["question"].strip()


        if not question:

            return jsonify({
                "success": False,
                "error": "Question cannot be empty."
            }), 400


        result = process_question(
            question
        )


        return jsonify(
            result
        )


    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )