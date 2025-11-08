# BARD/src/agent/tools/__init__.py
from .retriever import set_project_files_retriever, get_project_files_retriever
from .search_project_files import search_project_files
from .get_godot_info import get_godot_info
from .code_generation import generate_and_refine_code


def get_tools():
	"""
	Returns a list of available tools for the agent.
	
	Returns:
		List of tool instances.
	"""
	return [
		search_project_files,
		get_godot_info,
		generate_and_refine_code
	]


__all__ = [
	"set_project_files_retriever",
	"get_project_files_retriever",
	"search_project_files",
	"get_godot_info",
	"generate_and_refine_code",
	"get_tools"
]