# BARD/src/lib.py

# TODO: Determine best place for system prompt. Not here, not constants. Maybe a json file?
SYSTEM_PROMPT = """
You are an expert game developer familiar with Godot engine.
"""

def get_system_prompt():
    return SYSTEM_PROMPT