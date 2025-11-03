# BARD/src/web_app/router.py
from flask import render_template, request, jsonify
import uuid
from datetime import datetime, timedelta
from langchain_core.messages import AIMessage

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
	def _extract_text_from_message(message):
		"""
		Extract text content from a message, handling tool calls properly.
		
		Args:
			message: A LangChain message object
			
		Returns:
			String containing the text content
		"""
		# If it's an AIMessage, handle content specially
		if isinstance(message, AIMessage):
			content = message.content
			
			# If content is a list (tool calls), extract text blocks
			if isinstance(content, list):
				text_parts = []
				for block in content:
					if isinstance(block, dict) and block.get("type") == "text":
						text_parts.append(block.get("text", ""))
					elif hasattr(block, "text"):
						text_parts.append(block.text)
				return " ".join(text_parts).strip()
			
			# If content is already a string, return it
			elif isinstance(content, str):
				return content
			
			# Fallback: try to convert to string
			return str(content)
		
		# For other message types, just get content
		return str(message.content) if hasattr(message, 'content') else str(message)
	
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
				last_message = result["messages"][-1]
				response_text = Router._extract_text_from_message(last_message)
				
				# If we got an empty response, provide a fallback
				if not response_text or response_text.strip() == "":
					response_text = "I processed your request but don't have a text response. The tool may have been called successfully."
				
				return jsonify({
					"response": response_text,
					"session_id": session_id
				})

			except Exception as e:
				import traceback
				traceback.print_exc()
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