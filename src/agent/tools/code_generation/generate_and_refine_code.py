# BARD/src/agent/tools/code_generation/generate_and_refine_code.py
import os
import re
from pathlib import Path
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from ..retriever import get_project_files_retriever
from .code_generator import generate_and_refine
from .helpers import get_project_structure_summary
from constants import BARD_OUTPUT_DIR, GODOT_VERSION


@tool
def generate_and_refine_code(request: str) -> str:
	"""
	Generate code files (GDScript or scene files) with AI refinement and save them to the BARD directory.
	This tool creates new game code based on your requirements, automatically refining it for quality.
	
	Use this when the user wants to:
	- Create new GDScript files (.gd)
	- Create new scene files (.tscn)
	- Generate game components, systems, or features
	
	The tool will:
	1. Analyze the request and determine relevant project files
	2. Generate code with context from your project
	3. Refine the code through multiple rounds for quality
	4. Save the files to the BARD directory in your project
	
	Args:
		request: The user's code generation request. Should include what to create and ideally the filename(s).
			Examples: 
			- "Create a player controller script called player.gd"
			- "Generate an enemy AI system in enemy_ai.gd"
			- "Create a main menu scene as main_menu.tscn"
	
	Returns:
		Status message with generation results and file locations.
	"""
	retriever = get_project_files_retriever()
	
	if retriever is None:
		return "Project files RAG is not initialized. Please check the configuration."
	
	# Get project path from environment
	project_path = os.getenv("PATH_TO_PROJECT_FILES")
	if not project_path:
		return "Error: Project path not configured."
	
	# Check if BARD directory exists
	bard_dir = Path(project_path) / BARD_OUTPUT_DIR
	if not bard_dir.exists():
		return f"Error: {BARD_OUTPUT_DIR} directory does not exist in project root. Please create it first."
	
	# Initialize LLM for analysis
	api_key = os.getenv("ANTHROPIC_API_KEY")
	if not api_key:
		return "Error: ANTHROPIC_API_KEY not configured."
	
	llm = ChatAnthropic(
		model="claude-sonnet-4-20250514",
		api_key=api_key,
		max_tokens=4096
	)
	
	# Step 1: Extract filenames from request
	filename_pattern = r'\b(\w+)\.(gd|tscn)\b'
	found_files = re.findall(filename_pattern, request)
	
	if not found_files:
		return """I need filename(s) to generate code. Please specify the filename(s) in your request.

Examples:
- "Create a player controller in player.gd"
- "Generate a main menu scene as main_menu.tscn"
- "Create enemy_ai.gd and enemy.tscn"

Supported file types: .gd (GDScript) and .tscn (scene files)"""
	
	files_to_generate = [(name, f".{ext}") for name, ext in found_files]
	
	# Step 2: Get project structure summary
	try:
		project_structure = get_project_structure_summary(Path(project_path))
	except Exception as e:
		project_structure = f"Error getting project structure: {e}"
	
	# Step 3: Use LLM to suggest which files to retrieve
	analysis_prompt = f"""Analyze this code generation request and suggest which existing project files would be most relevant as context.

Request: {request}

Project Structure:
{project_structure}

Files to generate: {', '.join([name + ext for name, ext in files_to_generate])}

List 2-4 specific filenames or file patterns that would be most relevant to retrieve from the project.
Respond with just the filenames or patterns, one per line, or "NONE" if no existing files are needed."""

	analysis_messages = [
		SystemMessage(content="You are a Godot project analyst."),
		HumanMessage(content=analysis_prompt)
	]
	
	analysis_response = llm.invoke(analysis_messages)
	suggested_files = analysis_response.content.strip()
	
	# Step 4: Retrieve relevant context
	if suggested_files.upper() != "NONE":
		context_parts = [f"Project Structure:\n{project_structure}\n"]
		
		# Retrieve suggested files
		for suggested in suggested_files.split('\n'):
			suggested = suggested.strip()
			if suggested and not suggested.upper().startswith("NONE"):
				try:
					retrieved = retriever.retrieve(suggested, k=2)
					context_parts.append(f"\nRelevant files for '{suggested}':\n{retrieved}\n")
				except Exception as e:
					context_parts.append(f"\nCould not retrieve '{suggested}': {e}\n")
		
		context = "\n".join(context_parts)
	else:
		context = f"Project Structure:\n{project_structure}\n\nNo existing files retrieved."
	
	# Step 5: Generate and refine each file
	results = []
	generated_files = []
	failed_files = []
	
	for filename, extension in files_to_generate:
		full_filename = filename + extension
		results.append(f"\n{'='*60}")
		results.append(f"Generating: {full_filename}")
		results.append(f"{'='*60}")
		
		try:
			# Generate and refine code
			code, is_valid, status = generate_and_refine(
				prompt=request,
				context=context,
				file_extension=extension,
				api_key=api_key
			)
			
			results.append(status)
			
			if is_valid:
				# Save to BARD directory
				output_path = bard_dir / full_filename
				with open(output_path, 'w', encoding='utf-8') as f:
					f.write(code)
				
				results.append(f"✓ Successfully saved to: {output_path}")
				generated_files.append(full_filename)
			else:
				results.append(f"✗ Validation failed for {full_filename}")
				failed_files.append((full_filename, code, status))
		
		except Exception as e:
			results.append(f"✗ Error generating {full_filename}: {e}")
			failed_files.append((full_filename, None, str(e)))
	
	# Step 6: Format final response
	summary = ["\n" + "="*60]
	summary.append("GENERATION SUMMARY")
	summary.append("="*60)
	
	if generated_files:
		summary.append(f"\n✓ Successfully generated {len(generated_files)} file(s):")
		for filename in generated_files:
			summary.append(f"  - {filename}")
	
	if failed_files:
		summary.append(f"\n✗ Failed to generate {len(failed_files)} file(s):")
		for filename, code, error in failed_files:
			summary.append(f"  - {filename}")
			summary.append(f"    Reason: {error[:100]}...")
			if code:
				summary.append(f"    Would you like me to save the generated code anyway?")
	
	summary.append(f"\nFiles location: {bard_dir}")
	summary.append("="*60)
	
	return "\n".join(results + summary)