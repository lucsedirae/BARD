# BARD/src/agent/tools/search_project_files.py
from langchain_core.tools import tool
from .retriever import get_project_files_retriever


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
	retriever = get_project_files_retriever()
	
	if retriever is None:
		return "Project files RAG is not initialized. Please check the configuration."
	
	return retriever.retrieve(query, k=3)