"""ChromaDB-backed knowledge store used by the Knowledge Studio (RAG).

The Chroma client and the default embedding model (all-MiniLM-L6-v2) are
created lazily on first use, so importing this module (e.g. when starting the
API or running tests) does not touch the disk or download model weights.
"""

import logging
import threading
from typing import Optional

from config import CHROMA_COLLECTION, CHROMA_DB_DIR

logger = logging.getLogger(__name__)


class RAGManager:
    def __init__(self, db_dir: str = CHROMA_DB_DIR, collection_name: str = CHROMA_COLLECTION):
        self.db_dir = db_dir
        self.collection_name = collection_name
        self._collection = None
        self._lock = threading.Lock()

    @property
    def collection(self):
        """Return the Chroma collection, creating the client on first access."""
        if self._collection is None:
            with self._lock:
                if self._collection is None:
                    import chromadb
                    from chromadb.utils import embedding_functions

                    logger.info("Opening ChromaDB at %s (collection=%s)", self.db_dir, self.collection_name)
                    client = chromadb.PersistentClient(path=self.db_dir)
                    self._collection = client.get_or_create_collection(
                        name=self.collection_name,
                        embedding_function=embedding_functions.DefaultEmbeddingFunction(),
                    )
        return self._collection

    def add_document(self, doc_id: str, content: str, metadata: Optional[dict] = None) -> None:
        """Insert or replace a document by id."""
        if not content or not content.strip():
            raise ValueError("Document content must not be empty")
        # Chroma rejects empty metadata dicts on some versions; pass None instead.
        metadata = metadata or None
        # upsert replaces an existing document with the same id atomically.
        self.collection.upsert(documents=[content], metadatas=[metadata] if metadata else None, ids=[doc_id])

    def query(self, query_text: str, n_results: int = 3) -> dict:
        """Return the ``n_results`` most similar documents to ``query_text``."""
        if not query_text or not query_text.strip():
            raise ValueError("Query text must not be empty")
        return self.collection.query(query_texts=[query_text], n_results=n_results)


rag_manager = RAGManager()
