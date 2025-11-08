# BARD/src/agent/tools/retriever.py
from typing import Optional


# Global retriever instance (will be set during initialization)
_project_files_retriever: Optional[object] = None


def set_project_files_retriever(retriever) -> None:
	"""
	Set the project files retriever instance.
	Called during application initialization.
	
	Args:
		retriever: RAGRetriever instance for project files
	"""
	global _project_files_retriever
	_project_files_retriever = retriever


def get_project_files_retriever():
	"""
	Get the current project files retriever instance.
	
	Returns:
		The RAGRetriever instance, or None if not initialized
	"""
	return _project_files_retriever