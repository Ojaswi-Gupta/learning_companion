from fastembed import TextEmbedding
from config import EMBED_MODEL

model_name = "sentence-transformers/" + EMBED_MODEL if "sentence-transformers/" not in EMBED_MODEL else EMBED_MODEL
model = TextEmbedding(model_name=model_name, threads=1)

def embed_texts(texts):
    # TextEmbedding returns an iterable of numpy arrays
    embeddings = list(model.embed(texts))
    return [e.tolist() for e in embeddings]


def embed_query(text):
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()