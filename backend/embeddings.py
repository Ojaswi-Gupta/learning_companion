import os
import logging
from functools import lru_cache
from huggingface_hub import InferenceClient
from config import EMBED_MODEL

logger = logging.getLogger(__name__)

HF_TOKEN = os.getenv("HF_TOKEN", "")
if not HF_TOKEN:
    print("Warning: HF_TOKEN is not set. Inference might fail.")

# By passing an empty string instead of None, we prevent it from searching the local ~ disk cache, preventing stale lockfile deadlocks.
client = InferenceClient(token=HF_TOKEN if HF_TOKEN else False)

model_name = "sentence-transformers/" + EMBED_MODEL if "sentence-transformers/" not in EMBED_MODEL else EMBED_MODEL

BATCH_SIZE = 10  # Process embeddings in batches to prevent API timeouts

def embed_texts(texts):
    """Embed a list of texts in batches for reliability."""
    all_embeddings = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        logger.info(f"Embedding batch {i//BATCH_SIZE + 1}/{(len(texts)-1)//BATCH_SIZE + 1} ({len(batch)} texts)")

        embeddings = client.feature_extraction(text=batch, model=model_name)

        if hasattr(embeddings, 'tolist'):
            all_embeddings.extend(embeddings.tolist())
        else:
            all_embeddings.extend(list(embeddings))

    return all_embeddings

@lru_cache(maxsize=64)
def embed_query(text):
    """Embed a single query text. Cached for repeated questions."""
    result = embed_texts([text])[0]
    # lru_cache needs hashable return, but callers expect a list
    return result