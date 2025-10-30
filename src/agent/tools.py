# BARD/src/agent/tools.py
from langchain_core.tools import tool
from typing import Optional


# Global retriever instance (will be set during initialization)
_project_files_retriever: Optional[object] = None


def set_project_files_retriever(retriever):
	"""
	Set the project files retriever instance.
	Called during application initialization.
	
	Args:
		retriever: RAGRetriever instance for project files
	"""
	global _project_files_retriever
	_project_files_retriever = retriever


@tool
def search_project_files(query: str) -> str:
	"""
	Search through the local Godot project files to find relevant code, scenes, and resources.
	Use this tool when the user asks about their specific project implementation, code structure,
	or wants to understand what files exist in their project.
	
	Args:
		query: The search query describing what to look for in the project files.
	
	Returns:
		Relevant file contents from the project.
	"""
	if _project_files_retriever is None:
		return "Project files RAG is not initialized. Please check the configuration."
	
	return _project_files_retriever.retrieve(query, k=3)


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


def get_tools():
	"""
	Returns a list of available tools for the agent.
	
	Returns:
		List of tool instances.
	"""
	return [search_project_files, get_godot_info]