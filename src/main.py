# BARD/src/main.py
from os import getenv
from flask import Flask
from agent import create_agent_graph
from web_app.router import Router


# Validate API key
api_key = getenv("ANTHROPIC_API_KEY")
if not api_key:
	raise ValueError("ANTHROPIC_API_KEY environment variable is required")

# Initialize LangGraph agent
agent_graph = create_agent_graph(api_key=api_key)

# Initialize Flask app
app = Flask(__name__)
Router.register_routes(app, agent_graph)

# Run the Flask app
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)