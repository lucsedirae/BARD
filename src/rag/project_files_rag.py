# BARD/src/rag/project_files_rag.py
from pathlib import Path
from typing import List
from .base import BaseRAG


class ProjectFilesRAG(BaseRAG):
	"""
	RAG implementation for indexing Godot project files.
	Handles GDScript, scene files, resources, and configuration files.
	"""
	
	def __init__(self, project_path: str, embedding_model: str = "all-MiniLM-L6-v2"):
		"""
		Initialize the project files RAG.
		
		Args:
			project_path: Path to the Godot project root
			embedding_model: Sentence transformer model name
		"""
		super().__init__(project_path, embedding_model)
		
	def get_file_extensions(self) -> List[str]:
		"""
		Define Godot-related file extensions to index.
		
		Returns:
			List of file extensions
		"""
		return [
			'.gd',        # GDScript files
			'.tscn',      # Scene files
			'.tres',      # Text resource files
			'.res',       # Binary resource files (will skip if binary)
			'.godot',     # Project configuration
			'.cfg',       # Configuration files
			'.import',    # Import configuration files
		]
	
	def should_include_file(self, file_path: Path) -> bool:
		"""
		Additional filtering for Godot project files.
		
		Args:
			file_path: Path to the file being considered
			
		Returns:
			True if file should be indexed
		"""
		# Skip hidden directories and files
		if any(part.startswith('.') for part in file_path.parts):
			# Exception: allow .godot file itself and .import files
			if file_path.name not in ['project.godot'] and not file_path.name.endswith('.import'):
				return False
		
		# Skip common directories to ignore
		ignore_dirs = {'.godot', 'addons', '.import', '__pycache__'}
		if any(ignored in file_path.parts for ignored in ignore_dirs):
			return False
		
		# Skip binary .res files (they're not human-readable)
		if file_path.suffix == '.res':
			try:
				with open(file_path, 'r', encoding='utf-8') as f:
					f.read(100)  # Try reading first 100 chars
			except UnicodeDecodeError:
				return False  # Binary file, skip it
		
		return True
	
	def preprocess_content(self, content: str, file_path: Path) -> str:
		"""
		Preprocess Godot file content before indexing.
		
		Args:
			content: Raw file content
			file_path: Path to the file
			
		Returns:
			Preprocessed content
		"""
		# Add file metadata as context for better search
		metadata = f"File: {file_path.name}\nPath: {file_path}\nType: {file_path.suffix}\n\n"
		
		# For scene files, add a note about it being a scene
		if file_path.suffix == '.tscn':
			metadata += "[Godot Scene File]\n\n"
		elif file_path.suffix == '.gd':
			metadata += "[GDScript File]\n\n"
		elif file_path.suffix == '.tres':
			metadata += "[Godot Resource File]\n\n"
		
		return metadata + content