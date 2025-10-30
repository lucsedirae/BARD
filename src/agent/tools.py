# BARD/src/agent/tools.py
from langchain_core.tools import tool


@tool
def get_godot_info(query: str) -> str:
	"""
	Placeholder tool for retrieving Godot engine information.
	
	Args:
		query: The information query about Godot engine.
	
	Returns:
		A placeholder response string.
	"""
	# TODO: Implement actual Godot documentation search or API calls
	return f"Placeholder response for query: '{query}'. This tool will be implemented later."


def get_tools():
	"""
	Returns a list of available tools for the agent.
	
	Returns:
		List of tool instances.
	"""
	return [get_godot_info]