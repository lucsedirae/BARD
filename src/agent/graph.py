# BARD/src/agent/graph.py
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from .state import AgentState
from .nodes import (
	process_input_node,
	llm_node,
	tool_execution_node,
	should_continue,
	format_response_node
)
from .tools import get_tools
from functools import partial


def create_agent_graph(api_key: str):
	"""
	Creates and compiles the LangGraph agent.
	
	Args:
		api_key: Anthropic API key for Claude.
	
	Returns:
		Compiled LangGraph instance ready to process requests.
	"""
	# Initialize Claude with tools
	tools = get_tools()
	llm = ChatAnthropic(
		model="claude-sonnet-4-20250514",
		api_key=api_key,
		max_tokens=4096
	).bind_tools(tools)
	
	# Create the graph
	workflow = StateGraph(AgentState)
	
	# Add nodes
	workflow.add_node("process_input", process_input_node)
	workflow.add_node("llm", partial(llm_node, llm=llm))
	workflow.add_node("tools", tool_execution_node)
	workflow.add_node("format_response", format_response_node)
	
	# Define the flow
	workflow.set_entry_point("process_input")
	workflow.add_edge("process_input", "llm")
	
	# Add conditional edge: if LLM calls tools, execute them, otherwise format response
	workflow.add_conditional_edges(
		"llm",
		should_continue,
		{
			"tools": "tools",
			"end": "format_response"
		}
	)
	
	# After executing tools, go back to LLM with results
	workflow.add_edge("tools", "llm")
	
	# Format response leads to END
	workflow.add_edge("format_response", END)
	
	# Compile and return
	return workflow.compile()