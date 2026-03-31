import os
from dotenv import load_dotenv

load_dotenv()

# ---------- LLM ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# ---------- Embeddings ----------
EMBED_MODEL = "all-MiniLM-L6-v2"
EMBED_DIM = 384
TOP_K = int(os.getenv("TOP_K", "20"))

# ---------- Supabase ----------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

# ---------- Upload ----------
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "1.0"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
ALLOWED_EXTENSIONS = {".pdf"}
