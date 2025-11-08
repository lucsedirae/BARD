# BARD/src/agent/tools/get_godot_info.py
from langchain_core.tools import tool


@tool
def get_godot_info(query: str) -> str:
	"""
	Placeholder tool for retrieving Godot engine documentation and API information.
	
	Args:
		query: The information query about Godot engine.
	
	Returns:
		A placeholder response string.
	"""
	# TODO: Implement actual Godot documentation RAG
	return f"Placeholder response for query: '{query}'. This tool will be implemented later."