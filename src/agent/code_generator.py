# BARD/src/agent/code_generator.py
from typing import Tuple, Dict
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from .validators import is_parseable, format_validation_errors
from constants import GODOT_VERSION, MAX_REFINEMENT_ROUNDS


def generate_code(
	prompt: str,
	context: str,
	file_extension: str,
	godot_version: str,
	llm: ChatAnthropic
) -> str:
	"""
	Generate initial code based on prompt and context.
	
	Args:
		prompt: User's code generation request
		context: Relevant project files and structure
		file_extension: Target file type (.gd or .tscn)
		godot_version: Version of Godot being used
		llm: ChatAnthropic instance
	
	Returns:
		Generated code as string
	"""
	file_type = "GDScript" if file_extension == ".gd" else "Godot scene file"
	
	system_prompt = f"""You are an expert Godot {godot_version} developer.
Generate clean, well-structured {file_type} code following best practices.
Use tabs for indentation, not spaces.
Follow the DRY (Don't Repeat Yourself) principle.
Include helpful comments explaining the code."""

	user_message = f"""Generate a {file_type} for the following request:

{prompt}

Project Context:
{context}

Generate ONLY the code, with no additional explanation or markdown formatting.
The code should be ready to save directly to a {file_extension} file."""

	messages = [
		SystemMessage(content=system_prompt),
		HumanMessage(content=user_message)
	]
	
	response = llm.invoke(messages)
	return response.content


def refine_code(
	code: str,
	file_extension: str,
	context: str,
	refinement_notes: str,
	llm: ChatAnthropic
) -> str:
	"""
	Refine existing code for better quality.
	
	Args:
		code: Code to refine
		file_extension: File type (.gd or .tscn)
		context: Project context
		refinement_notes: Specific issues to address
		llm: ChatAnthropic instance
	
	Returns:
		Refined code as string
	"""
	file_type = "GDScript" if file_extension == ".gd" else "Godot scene file"
	
	system_prompt = f"""You are an expert code reviewer and Godot developer.
Improve the provided {file_type} code by:
1. Improving readability with clear variable names and comments
2. Following DRY principles to eliminate duplication
3. Integrating with existing project patterns shown in the context
4. Ensuring proper structure and organization
5. Using tabs for indentation

Maintain the core functionality while improving quality."""

	user_message = f"""Refine this {file_type} code:

```
{code}
```

Project Context:
{context}

{refinement_notes}

Return ONLY the improved code, with no explanation or markdown formatting."""

	messages = [
		SystemMessage(content=system_prompt),
		HumanMessage(content=user_message)
	]
	
	response = llm.invoke(messages)
	return response.content


def assess_code_quality(
	code: str,
	file_extension: str,
	llm: ChatAnthropic
) -> Tuple[bool, str]:
	"""
	Assess if code meets quality threshold.
	
	Args:
		code: Code to assess
		file_extension: File type (.gd or .tscn)
		llm: ChatAnthropic instance
	
	Returns:
		Tuple of (meets_threshold, assessment_notes)
	"""
	file_type = "GDScript" if file_extension == ".gd" else "Godot scene file"
	
	system_prompt = """You are a code quality assessor.
Evaluate code quality based on:
- Readability (clear names, proper comments)
- DRY principles (no unnecessary duplication)
- Proper structure and organization
- Best practices for the file type

Respond with ONLY 'PASS' or 'FAIL' followed by a brief explanation."""

	user_message = f"""Assess the quality of this {file_type}:

```
{code}
```

Does this code meet professional quality standards?"""

	messages = [
		SystemMessage(content=system_prompt),
		HumanMessage(content=user_message)
	]
	
	response = llm.invoke(messages)
	assessment = response.content.strip()
	
	# Check if assessment starts with PASS
	meets_threshold = assessment.upper().startswith('PASS')
	
	return meets_threshold, assessment


def generate_and_refine(
	prompt: str,
	context: str,
	file_extension: str,
	api_key: str
) -> Tuple[str, bool, str]:
	"""
	Generate code and refine it through multiple rounds.
	
	Args:
		prompt: User's code generation request
		context: Relevant project files and structure
		file_extension: Target file type (.gd or .tscn)
		api_key: Anthropic API key
	
	Returns:
		Tuple of (final_code, is_valid, status_message)
	"""
	llm = ChatAnthropic(
		model="claude-sonnet-4-20250514",
		api_key=api_key,
		max_tokens=4096
	)
	
	# Initial generation
	code = generate_code(prompt, context, file_extension, GODOT_VERSION, llm)
	
	# Validate initial code
	is_valid, errors = is_parseable(code, file_extension)
	if not is_valid:
		validation_errors = format_validation_errors(errors)
		return code, False, f"Initial generation failed validation:\n{validation_errors}"
	
	# Refinement loop
	refinement_round = 0
	status_messages = ["Initial code generated successfully"]
	
	while refinement_round < MAX_REFINEMENT_ROUNDS:
		refinement_round += 1
		
		# Assess current quality
		meets_threshold, assessment = assess_code_quality(code, file_extension, llm)
		status_messages.append(f"Round {refinement_round} assessment: {assessment}")
		
		if meets_threshold:
			status_messages.append(f"Quality threshold met after {refinement_round} round(s)")
			break
		
		# Refine code
		refinement_notes = f"Issues to address: {assessment}"
		code = refine_code(code, file_extension, context, refinement_notes, llm)
		
		# Validate refined code
		is_valid, errors = is_parseable(code, file_extension)
		if not is_valid:
			validation_errors = format_validation_errors(errors)
			status_messages.append(f"Refinement round {refinement_round} failed validation")
			return code, False, "\n".join(status_messages) + f"\n{validation_errors}"
		
		status_messages.append(f"Round {refinement_round} refinement completed")
	
	if refinement_round >= MAX_REFINEMENT_ROUNDS:
		status_messages.append(f"Maximum refinement rounds ({MAX_REFINEMENT_ROUNDS}) reached")
	
	return code, True, "\n".join(status_messages)