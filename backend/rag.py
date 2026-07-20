import os
import chromadb
from chromadb.utils import embedding_functions

# Use default local embedding function (all-MiniLM-L6-v2)
default_ef = embedding_functions.DefaultEmbeddingFunction()

DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

class RAGManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_DIR)
        self.collection = self.client.get_or_create_collection(
            name="knowledge_store", 
            embedding_function=default_ef
        )

    def add_document(self, doc_id: str, content: str, metadata: dict = None):
        if metadata is None:
            metadata = {}
        # Remove if exists to allow updating
        try:
            self.collection.delete(ids=[doc_id])
        except Exception:
            pass
            
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query(self, query_text: str, n_results: int = 3):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

rag_manager = RAGManager()
