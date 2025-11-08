# BARD/src/agent/tools/code_generation/validators.py
import re
from typing import Tuple, List


def validate_gdscript(code: str) -> Tuple[bool, List[str]]:
	"""
	Validate GDScript code for common syntax errors.
	
	Args:
		code: GDScript code as a string
	
	Returns:
		Tuple of (is_valid, list_of_errors)
	"""
	errors = []
	
	if not code or not code.strip():
		return False, ["Code is empty"]
	
	lines = code.split('\n')
	
	# Check for extends keyword (should be present in most scripts)
	has_extends = any(line.strip().startswith('extends ') for line in lines)
	if not has_extends:
		errors.append("Warning: No 'extends' keyword found - may not be a valid GDScript class")
	
	# Check for common syntax errors
	for i, line in enumerate(lines, 1):
		stripped = line.strip()
		
		# Skip empty lines and comments
		if not stripped or stripped.startswith('#'):
			continue
		
		# Check for function definitions missing colon
		if stripped.startswith('func ') and not stripped.endswith(':'):
			if '(' in stripped and ')' in stripped:
				errors.append(f"Line {i}: Function definition missing colon")
		
		# Check for control structures missing colon
		for keyword in ['if ', 'elif ', 'else:', 'for ', 'while ', 'match ']:
			if stripped.startswith(keyword) and keyword != 'else:':
				if not stripped.endswith(':'):
					errors.append(f"Line {i}: '{keyword.strip()}' statement missing colon")
		
		# Check for common indentation issues (mixing tabs/spaces)
		if line.startswith(' ') and '\t' in line[:len(line) - len(line.lstrip())]:
			errors.append(f"Line {i}: Mixed tabs and spaces in indentation")
	
	# Check for balanced parentheses and brackets
	if code.count('(') != code.count(')'):
		errors.append("Unbalanced parentheses")
	if code.count('[') != code.count(']'):
		errors.append("Unbalanced square brackets")
	if code.count('{') != code.count('}'):
		errors.append("Unbalanced curly braces")
	
	return len(errors) == 0, errors


def validate_tscn(content: str) -> Tuple[bool, List[str]]:
	"""
	Validate .tscn scene file format.
	
	Args:
		content: Scene file content as a string
	
	Returns:
		Tuple of (is_valid, list_of_errors)
	"""
	errors = []
	
	if not content or not content.strip():
		return False, ["Scene file is empty"]
	
	lines = content.split('\n')
	
	# Check for [gd_scene] header
	has_header = False
	for line in lines[:10]:  # Check first 10 lines
		if line.strip().startswith('[gd_scene'):
			has_header = True
			break
	
	if not has_header:
		errors.append("Missing [gd_scene] header")
	
	# Check for basic scene structure
	has_node = any('[node' in line for line in lines)
	if not has_node:
		errors.append("Warning: No [node] sections found - scene may be empty")
	
	# Check for balanced quotes in resource definitions
	quote_count = content.count('"')
	if quote_count % 2 != 0:
		errors.append("Unbalanced quotes in scene file")
	
	return len(errors) == 0, errors


def is_parseable(content: str, file_extension: str) -> Tuple[bool, List[str]]:
	"""
	General validation dispatcher based on file type.
	
	Args:
		content: File content as a string
		file_extension: File extension (e.g., '.gd', '.tscn')
	
	Returns:
		Tuple of (is_valid, list_of_errors)
	"""
	if file_extension == '.gd':
		return validate_gdscript(content)
	elif file_extension == '.tscn':
		return validate_tscn(content)
	else:
		return False, [f"Unsupported file type: {file_extension}"]


def format_validation_errors(errors: List[str]) -> str:
	"""
	Format validation errors into a readable string.
	
	Args:
		errors: List of error messages
	
	Returns:
		Formatted error string
	"""
	if not errors:
		return "No errors found"
	
	return "Validation Errors:\n" + "\n".join(f"  • {error}" for error in errors)