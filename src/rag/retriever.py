# BARD/src/rag/retriever.py
from typing import List, Dict
from .base import BaseRAG


class RAGRetriever:
	"""
	Wrapper for BaseRAG implementations to provide a clean interface
	for LangChain tool integration.
	"""
	
	def __init__(self, rag: BaseRAG):
		"""
		Initialize the retriever with a RAG instance.
		
		Args:
			rag: BaseRAG implementation (e.g., ProjectFilesRAG)
		"""
		self.rag = rag
	
	def retrieve(self, query: str, k: int = 3) -> str:
		"""
		Retrieve relevant documents and format them for the LLM.
		
		Args:
			query: Search query
			k: Number of documents to retrieve
			
		Returns:
			Formatted string with retrieved document contents
		"""
		if self.rag.get_document_count() == 0:
			return "No documents have been indexed yet."
		
		# Perform hybrid search
		results = self.rag.hybrid_search(query, k=k)
		
		if not results:
			return f"No relevant documents found for query: '{query}'"
		
		# Format results
		formatted_results = []
		for i, doc in enumerate(results, 1):
			formatted_results.append(
				f"--- Document {i}: {doc['path']} ---\n"
				f"{doc['content']}\n"
				f"--- End of {doc['filename']} ---\n"
			)
		
		return "\n".join(formatted_results)
	
	def get_stats(self) -> Dict[str, int]:
		"""
		Get statistics about the indexed documents.
		
		Returns:
			Dictionary with indexing statistics
		"""
		return {
			"total_documents": self.rag.get_document_count()
		}