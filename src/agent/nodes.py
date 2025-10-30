# BARD/src/agent/nodes.py
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from .state import AgentState
from .tools import get_tools
import lib


def process_input_node(state: AgentState) -> AgentState:
	"""
	Processes the incoming user input and prepares it for the LLM.
	
	Args:
		state: Current agent state.
	
	Returns:
		Updated state with user message added to history.
	"""
	user_message = HumanMessage(content=state["current_input"])
	return {
		"messages": [user_message]
	}


def llm_node(state: AgentState, llm: ChatAnthropic) -> AgentState:
	"""
	Calls the LLM (Claude) with the conversation history and available tools.
	
	Args:
		state: Current agent state.
		llm: The ChatAnthropic instance with bound tools.
	
	Returns:
		Updated state with LLM response added to messages.
	"""
	# Prepare messages with system prompt
	system_message = SystemMessage(content=lib.get_system_prompt())
	messages = [system_message] + list(state["messages"])
	
	# Invoke LLM
	response = llm.invoke(messages)
	
	return {
		"messages": [response]
	}


def format_response_node(state: AgentState) -> AgentState:
	"""
	Formats the final response from the agent.
	
	Args:
		state: Current agent state.
	
	Returns:
		State with no modifications (response is already in messages).
	"""
	# Response is already in the messages list
	# This node exists as a placeholder for future response formatting logic
	return state