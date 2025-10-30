# BARD/src/rag/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
import os
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class BaseRAG(ABC):
	"""
	Abstract base class for RAG implementations.
	Provides common functionality for indexing, embedding, and hybrid search.
	"""
	
	def __init__(self, base_path: str, embedding_model: str = "all-MiniLM-L6-v2"):
		"""
		Initialize the RAG system.
		
		Args:
			base_path: Root directory to index
			embedding_model: Name of the sentence-transformers model to use
		"""
		self.base_path = Path(base_path)
		self.embedding_model = SentenceTransformer(embedding_model)
		self.documents: List[Dict[str, str]] = []
		self.index = None
		self.embeddings = None
		
	@abstractmethod
	def get_file_extensions(self) -> List[str]:
		"""
		Define which file extensions to index.
		
		Returns:
			List of file extensions (e.g., ['.gd', '.tscn'])
		"""
		pass
	
	@abstractmethod
	def should_include_file(self, file_path: Path) -> bool:
		"""
		Additional filtering logic for files.
		
		Args:
			file_path: Path to the file being considered
			
		Returns:
			True if file should be indexed, False otherwise
		"""
		pass
	
	def preprocess_content(self, content: str, file_path: Path) -> str:
		"""
		Optional preprocessing of file content before indexing.
		Can be overridden by subclasses.
		
		Args:
			content: Raw file content
			file_path: Path to the file
			
		Returns:
			Preprocessed content
		"""
		return content
	
	def index_files(self) -> int:
		"""
		Index all files in the base path matching criteria.
		
		Returns:
			Number of files indexed
		"""
		self.documents = []
		extensions = self.get_file_extensions()
		
		# Walk through directory
		for root, _, files in os.walk(self.base_path):
			for file in files:
				file_path = Path(root) / file
				
				# Check extension and custom filter
				if file_path.suffix in extensions and self.should_include_file(file_path):
					try:
						with open(file_path, 'r', encoding='utf-8') as f:
							content = f.read()
						
						# Preprocess content
						processed_content = self.preprocess_content(content, file_path)
						
						# Store document
						relative_path = file_path.relative_to(self.base_path)
						self.documents.append({
							'path': str(relative_path),
							'full_path': str(file_path),
							'filename': file_path.name,
							'content': processed_content
						})
					except Exception as e:
						print(f"Error reading {file_path}: {e}")
		
		# Create embeddings and FAISS index
		if self.documents:
			texts = [doc['content'] for doc in self.documents]
			self.embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
			
			# Create FAISS index
			dimension = self.embeddings.shape[1]
			self.index = faiss.IndexFlatL2(dimension)
			self.index.add(self.embeddings.astype('float32'))
		
		return len(self.documents)
	
	def semantic_search(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
		"""
		Perform semantic search using FAISS.
		
		Args:
			query: Search query
			k: Number of results to return
			
		Returns:
			List of (document, distance) tuples
		"""
		if not self.index or not self.documents:
			return []
		
		# Embed query
		query_embedding = self.embedding_model.encode([query])
		
		# Search
		k = min(k, len(self.documents))
		distances, indices = self.index.search(query_embedding.astype('float32'), k)
		
		results = []
		for idx, distance in zip(indices[0], distances[0]):
			results.append((self.documents[idx], float(distance)))
		
		return results
	
	def keyword_search(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
		"""
		Perform keyword-based search on filenames and content.
		
		Args:
			query: Search query
			k: Number of results to return
			
		Returns:
			List of (document, score) tuples
		"""
		if not self.documents:
			return []
		
		query_lower = query.lower()
		query_terms = query_lower.split()
		
		scored_docs = []
		for doc in self.documents:
			score = 0.0
			
			# Filename matching (higher weight)
			filename_lower = doc['filename'].lower()
			if query_lower in filename_lower:
				score += 10.0
			for term in query_terms:
				if term in filename_lower:
					score += 5.0
			
			# Path matching
			path_lower = doc['path'].lower()
			if query_lower in path_lower:
				score += 3.0
			
			# Content matching (lower weight)
			content_lower = doc['content'].lower()
			for term in query_terms:
				score += content_lower.count(term) * 0.1
			
			if score > 0:
				scored_docs.append((doc, score))
		
		# Sort by score and return top k
		scored_docs.sort(key=lambda x: x[1], reverse=True)
		return scored_docs[:k]
	
	def hybrid_search(self, query: str, k: int = 5, semantic_weight: float = 0.7) -> List[Dict]:
		"""
		Combine semantic and keyword search with weighted scoring.
		
		Args:
			query: Search query
			k: Number of results to return
			semantic_weight: Weight for semantic search (0-1)
			
		Returns:
			List of documents ranked by combined score
		"""
		keyword_weight = 1.0 - semantic_weight
		
		# Get results from both methods
		semantic_results = self.semantic_search(query, k=k*2)
		keyword_results = self.keyword_search(query, k=k*2)
		
		# Normalize and combine scores
		doc_scores: Dict[str, Tuple[Dict, float]] = {}
		
		# Process semantic results (lower distance = better, so invert)
		if semantic_results:
			max_distance = max(dist for _, dist in semantic_results)
			for doc, distance in semantic_results:
				normalized_score = (max_distance - distance) / max_distance if max_distance > 0 else 1.0
				doc_scores[doc['path']] = (doc, normalized_score * semantic_weight)
		
		# Process keyword results
		if keyword_results:
			max_score = max(score for _, score in keyword_results)
			for doc, score in keyword_results:
				normalized_score = score / max_score if max_score > 0 else 1.0
				path = doc['path']
				if path in doc_scores:
					# Add to existing score
					doc_scores[path] = (doc, doc_scores[path][1] + normalized_score * keyword_weight)
				else:
					doc_scores[path] = (doc, normalized_score * keyword_weight)
		
		# Sort by combined score and return top k
		ranked_docs = sorted(doc_scores.values(), key=lambda x: x[1], reverse=True)
		return [doc for doc, _ in ranked_docs[:k]]
	
	def get_document_count(self) -> int:
		"""Returns the number of indexed documents."""
		return len(self.documents)