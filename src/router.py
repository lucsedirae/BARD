# BARD/src/router.py
from flask import render_template, request, jsonify
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/chat', methods=['POST'])
    def chat():
        user_message = request.json.get('message', '')
        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": user_message}]}
            )
            return jsonify({'response': str(response)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500