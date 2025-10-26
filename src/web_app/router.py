# BARD/src/router.py
from flask import render_template, request, jsonify
import lib


class Router:
    @staticmethod
    def register_routes(app, agent):
        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/chat", methods=["POST"])
        def chat():
            try:
                user_message = request.json.get("message") if request.json else None

                if not user_message:
                    return jsonify({"error": "No message provided"}), 400
                
                message = agent.messages.create(
                    model="claude-2",
                    max_tokens_to_sample=1000,
                    messages=[
                        {"role": "system", "content": lib.get_system_prompt()},
                        {"role": "user", "content": user_message},
                    ],
                )
                
                response_text = message.choices[0].message['content']
                return jsonify({"response": response_text})
            
            except Exception as e:
                return jsonify({"error": str(e)}), 500