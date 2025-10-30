# BARD/src/agent/state.py
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from operator import add


class AgentState(TypedDict):
	"""
	State schema for the BARD agent.
	
	Attributes:
		messages: List of conversation messages (user and assistant).
			Uses add operator to append new messages to history.
		current_input: The current user input being processed.
		session_id: Unique identifier for the conversation session.
	"""
	messages: Annotated[Sequence[BaseMessage], add]
	current_input: str
	session_id: str