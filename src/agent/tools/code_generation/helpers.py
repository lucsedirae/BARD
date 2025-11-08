# BARD/src/agent/tools/code_generation/helpers.py
import os
from pathlib import Path


def get_project_structure_summary(project_path: Path) -> str:
	"""
	Generate a summary of the project's file structure.
	
	Args:
		project_path: Path to the project root
	
	Returns:
		Formatted string with directory structure
	"""
	structure_lines = ["Project Directory Structure:"]
	
	try:
		# Walk through project directory
		ignore_dirs = {'.godot', '.git', '__pycache__', 'addons', '.import'}
		
		for root, dirs, files in os.walk(project_path):
			# Filter out ignored directories
			dirs[:] = [d for d in dirs if d not in ignore_dirs]
			
			level = root.replace(str(project_path), '').count(os.sep)
			indent = '  ' * level
			folder_name = os.path.basename(root) or project_path.name
			structure_lines.append(f"{indent}{folder_name}/")
			
			# Limit depth to avoid too much detail
			if level < 3:
				sub_indent = '  ' * (level + 1)
				for file in sorted(files)[:10]:  # Limit files per directory
					if not file.startswith('.'):
						structure_lines.append(f"{sub_indent}{file}")
				
				if len(files) > 10:
					structure_lines.append(f"{sub_indent}... and {len(files) - 10} more files")
	
	except Exception as e:
		structure_lines.append(f"Error reading structure: {e}")
	
	return "\n".join(structure_lines[:50])  # Limit total lines