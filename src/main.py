# BARD/src/main.py 
from os import getenv
from flask import Flask
from anthropic import Anthropic
from web_app.router import Router
from langchain.agents import create_agent
import lib


# Initialize Anthropic client
agent = Anthropic(api_key=getenv("ANTHROPIC_API_KEY"))

# Initialize Flask app
app = Flask(__name__)
Router.register_routes(app, agent)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)