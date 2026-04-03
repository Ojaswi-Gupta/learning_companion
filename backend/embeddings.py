import os
from huggingface_hub import InferenceClient
from config import EMBED_MODEL

HF_TOKEN = os.getenv("HF_TOKEN", "")
if not HF_TOKEN:
    print("Warning: HF_TOKEN is not set. Inference might fail.")

# By passing an empty string instead of None, we prevent it from searching the local ~ disk cache, preventing stale lockfile deadlocks.
client = InferenceClient(token=HF_TOKEN if HF_TOKEN else False)

model_name = "sentence-transformers/" + EMBED_MODEL if "sentence-transformers/" not in EMBED_MODEL else EMBED_MODEL

def embed_texts(texts):
    # The Hugging Face API handles lists of text and returns embeddings directly
    embeddings = client.feature_extraction(text=texts, model=model_name)
    
    # Convert numpy arrays to standard python lists if necessary
    if hasattr(embeddings, 'tolist'):
        return embeddings.tolist()
    return list(embeddings)

def embed_query(text):
    # Query expects exactly one float array back
    return embed_texts([text])[0]