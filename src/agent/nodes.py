# BARD/src/agent/nodes.py
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
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


def tool_execution_node(state: AgentState) -> AgentState:
	"""
	Executes any tool calls from the LLM's response.
	
	Args:
		state: Current agent state.
	
	Returns:
		Updated state with tool results added to messages.
	"""
	last_message = state["messages"][-1]
	
	# Check if there are tool calls
	if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
		return {"messages": []}
	
	# Get available tools
	tools = get_tools()
	tools_by_name = {tool.name: tool for tool in tools}
	
	# Execute each tool call
	tool_messages = []
	for tool_call in last_message.tool_calls:
		tool_name = tool_call["name"]
		tool_args = tool_call["args"]
		tool_call_id = tool_call["id"]
		
		if tool_name in tools_by_name:
			tool = tools_by_name[tool_name]
			try:
				# Execute the tool
				result = tool.invoke(tool_args)
				
				# Create tool result message
				tool_message = ToolMessage(
					content=str(result),
					tool_call_id=tool_call_id,
					name=tool_name
				)
				tool_messages.append(tool_message)
			except Exception as e:
				# Handle tool execution errors
				error_message = ToolMessage(
					content=f"Error executing {tool_name}: {str(e)}",
					tool_call_id=tool_call_id,
					name=tool_name
				)
				tool_messages.append(error_message)
		else:
			# Tool not found
			error_message = ToolMessage(
				content=f"Tool {tool_name} not found",
				tool_call_id=tool_call_id,
				name=tool_name
			)
			tool_messages.append(error_message)
	
	return {"messages": tool_messages}


def should_continue(state: AgentState) -> str:
	"""
	Determines if the agent should continue processing or end.
	
	Args:
		state: Current agent state.
	
	Returns:
		"tools" if there are tool calls to execute, "end" otherwise.
	"""
	last_message = state["messages"][-1]
	
	# Check if the last message has tool calls
	if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
		return "tools"
	
	return "end"


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