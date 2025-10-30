# BARD/src/web_app/router.py
from flask import render_template, request, jsonify
import uuid
from datetime import datetime, timedelta

from constants import (
	WEB_APP_TITLE, 
	WEB_HELLO_MESSAGE, 
	WEB_LOADING_MESSAGE
)


class Router:
	# In-memory session storage
	# Key: session_id, Value: {"state": AgentState, "last_access": datetime}
	sessions = {}
	SESSION_TIMEOUT = timedelta(hours=1)
	
	@staticmethod
	def _cleanup_old_sessions():
		"""Remove sessions that have timed out."""
		current_time = datetime.now()
		expired_sessions = [
			sid for sid, data in Router.sessions.items()
			if current_time - data["last_access"] > Router.SESSION_TIMEOUT
		]
		for sid in expired_sessions:
			del Router.sessions[sid]
	
	@staticmethod
	def _get_or_create_session(session_id: str = None):
		"""Get existing session or create a new one."""
		Router._cleanup_old_sessions()
		
		if session_id and session_id in Router.sessions:
			# Update last access time
			Router.sessions[session_id]["last_access"] = datetime.now()
			return session_id, Router.sessions[session_id]["state"]
		
		# Create new session
		new_session_id = str(uuid.uuid4())
		Router.sessions[new_session_id] = {
			"state": {"messages": [], "session_id": new_session_id},
			"last_access": datetime.now()
		}
		return new_session_id, Router.sessions[new_session_id]["state"]
	
	@staticmethod
	def register_routes(app, agent):
		"""
		Initializes the routes for the web app.

		Args:
			app (Flask): The Flask application instance.
			agent: The compiled LangGraph agent.

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
			Handles chat messages using the LangGraph agent.

			Returns:
				json: The JSON response containing the result of the chat.
			"""
			try:
				# Extract user message and session ID from the request
				data = request.json if request.json else {}
				user_message = data.get("message")
				session_id = data.get("session_id")
				
				if not user_message:
					return jsonify({"error": "No message provided"}), 400

				# Get or create session
				session_id, current_state = Router._get_or_create_session(session_id)
				
				# Prepare input state
				input_state = {
					**current_state,
					"current_input": user_message
				}
				
				# Invoke the agent
				result = agent.invoke(input_state)
				
				# Update session state
				Router.sessions[session_id]["state"] = {
					"messages": result["messages"],
					"session_id": session_id
				}
				
				# Extract the last message (agent's response)
				response_text = result["messages"][-1].content
				
				return jsonify({
					"response": response_text,
					"session_id": session_id
				})

			except Exception as e:
				return jsonify({"error": str(e)}), 500
		
		@app.route("/clear_session", methods=["POST"])
		def clear_session():
			"""
			Clears a specific session.

			Returns:
				json: Success message.
			"""
			try:
				data = request.json if request.json else {}
				session_id = data.get("session_id")
				
				if session_id and session_id in Router.sessions:
					del Router.sessions[session_id]
				
				return jsonify({"success": True})
			
			except Exception as e:
				return jsonify({"error": str(e)}), 500