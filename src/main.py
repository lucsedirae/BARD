# BARD/src/main.py 
from os import getenv
from flask import Flask
from web_app.router import Router
from langchain.agents import create_agent
import lib

# Create the agent with the system prompt from lib.py
agent = create_agent(
    model=getenv("DEFAULT_MODEL"),
    tools=[],
    system_prompt=lib.get_system_prompt(),
)
# Initialize Flask app
app = Flask(__name__)
Router.register_routes(app, agent)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)