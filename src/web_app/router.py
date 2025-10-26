# BARD/src/router.py
from flask import render_template, request, jsonify


class Router:
    @staticmethod
    def register_routes(app, agent):
        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/chat", methods=["POST"])
        def chat():
            user_message = request.json.get("message") if request.json else None

            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_message}]},
                context={"user_role": "expert"},
            )

            return jsonify({"response": result})
