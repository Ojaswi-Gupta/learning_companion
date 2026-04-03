"""Vector store backed by Supabase pgvector via the `vecs` library.

The vecs library automatically manages a pgvector collection (table)
in your Supabase Postgres database.
"""

import logging
from supabase_client import vecs_client
from config import EMBED_DIM, SCORE_THRESHOLD

logger = logging.getLogger(__name__)

COLLECTION_NAME = "document_chunks"


class VectorStore:
    """Manages a pgvector collection for document chunk embeddings."""

    def __init__(self):
        self.collection = None

    def _ensure_init(self):
        """Lazy load the collection if startup failed to connect."""
        if self.collection is None:
            self.collection = vecs_client.get_or_create_collection(
                name=COLLECTION_NAME,
                dimension=EMBED_DIM
            )
        return self.collection

    def init(self):
        """Get or create the pgvector collection forcefully."""
        self._ensure_init()

    def add_documents(self, texts, vectors):
        """Add document chunks and their vectors to the collection.

        Args:
            texts: list of dicts with keys: text, doc_id, file_name, page, etc.
            vectors: list of embedding vectors (lists of floats)
        """

        records = []
        for i, (meta, vec) in enumerate(zip(texts, vectors)):
            # vecs expects (id, vector, metadata)
            record_id = f"{meta['doc_id']}_{i}_{meta.get('page', 0)}"
            records.append((
                record_id,
                vec,
                {
                    "text": meta["text"],
                    "doc_id": meta["doc_id"],
                    "file_name": meta.get("file_name", ""),
                    "page": meta.get("page", 0)
                }
            ))

        self._ensure_init().upsert(records=records)

        # Create or refresh the index for fast search
        try:
            self._ensure_init().create_index(replace=True)
        except Exception as e:
            logger.warning(f"Index creation note: {e}")

    def search(self, vec, top_k=10):
        """Search the collection for the top-k most similar vectors.

        Returns a list of dicts with keys: text, doc_id, file_name, page, score
        """

        results = self._ensure_init().query(
            data=vec,
            limit=top_k,
            include_metadata=True,
            include_value=True
        )

        # vecs returns list of (id, distance, metadata) tuples
        docs = []
        for record_id, distance, metadata in results:
            if metadata:
                item = metadata.copy()
                item["score"] = float(distance)
                docs.append(item)

        return docs

    def delete_doc(self, doc_id):
        """Remove all chunks for a given doc_id using vecs filters."""
        try:
            self._ensure_init().delete(filters={"doc_id": {"$eq": doc_id}})
            logger.info(f"Deleted chunks for doc_id={doc_id}")
        except Exception as e:
            logger.error(f"Error deleting doc {doc_id}: {e}", exc_info=True)
            raise


# Module-level singleton so existing imports continue to work
store = VectorStore()


def load_index():
    store.init()

def add_documents(texts, vectors):
    store.add_documents(texts, vectors)

def search(vec, top_k=10):
    return store.search(vec, top_k)

def delete_doc(doc_id):
    store.delete_doc(doc_id)