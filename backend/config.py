import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL","llama-3.3-70b-versatile")

EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 20

INDEX_PATH = "data/index/index.faiss"
META_PATH = "data/index/meta.pkl"
DOC_STORE = "data/document_store.json"
UPLOAD_DIR = "data/uploads"
