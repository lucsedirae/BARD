# BARD/src/router.py
from flask import render_template, request, jsonify
import lib

from constants import (
    WEB_APP_TITLE, 
    WEB_HELLO_MESSAGE, 
    WEB_LOADING_MESSAGE
)

class Router:
    @staticmethod
    def register_routes(app, agent):
        """
        Initializes the routes for the web app.

        Args:
            app (Flask): The Flask application instance.
            agent (Anthropic): The Anthropic API client instance.

        Returns:
            json: The JSON response containing the result of the chat.
        """
        @app.route("/")
        def index():
            """
            Web app index.

            Returns:
                HTML: The rendered HTML template for the index page.
            """
            return render_template(
                "index.html", 
                title=WEB_APP_TITLE, 
                welcome_message=WEB_HELLO_MESSAGE,
                loading_message=WEB_LOADING_MESSAGE
            )

        @app.route("/chat", methods=["POST"])
        def chat():
            """
            Handles chat messages.

            Returns:
                json: The JSON response containing the result of the chat.
            """
            try:
                # Extract user message from the request
                user_message = request.json.get("message") if request.json else None
                if not user_message:
                    return jsonify({"error": "No message provided"}), 400

                # Create a message using the Anthropic client
                message = agent.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    system=lib.get_system_prompt(),
                    messages=[
                        {"role": "user", "content": user_message},
                    ],
                )

                # Extract the response text from the message
                response_text = message.content[0].text
                return jsonify({"response": response_text})

            except Exception as e:
                return jsonify({"error": str(e)}), 500
