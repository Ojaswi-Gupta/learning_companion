from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL

model = SentenceTransformer(EMBED_MODEL)


def embed_texts(texts):
    return model.encode(texts).tolist()


def embed_query(text):
    return model.encode([text])[0]