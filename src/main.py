# BARD/src/main.py
from os import getenv
from flask import Flask
from agent import create_agent_graph
from agent.tools import set_project_files_retriever
from web_app.router import Router
from rag import ProjectFilesRAG, RAGRetriever


# Validate API key
api_key = getenv("ANTHROPIC_API_KEY")
if not api_key:
	raise ValueError("ANTHROPIC_API_KEY environment variable is required")

# Get project path
project_path = getenv("PATH_TO_PROJECT_FILES")
if not project_path:
	raise ValueError("PATH_TO_PROJECT_FILES environment variable is required")

print(f"Initializing BARD with project path: {project_path}")

# Initialize RAG system
print("Indexing project files...")
project_rag = ProjectFilesRAG(project_path)
num_files = project_rag.index_files()
print(f"Indexed {num_files} project files")

# Create retriever and set it globally for tools
project_retriever = RAGRetriever(project_rag)
set_project_files_retriever(project_retriever)

# Initialize LangGraph agent
agent_graph = create_agent_graph(api_key=api_key)

# Initialize Flask app
app = Flask(__name__)
Router.register_routes(app, agent_graph)

# Run the Flask app
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)