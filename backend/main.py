from fastapi import FastAPI, UploadFile, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import logging

from ingest import ingest_pdf_bytes
from rag_pipeline import ask_question, clear_memory, general_llm_answer, get_all_topics
from vector_store import load_index, delete_doc
from documents_store import get_documents, delete_document
from config import MAX_UPLOAD_MB, ALLOWED_EXTENSIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-ID"]
)


@app.on_event("startup")
def startup():
    """Initialize the pgvector collection on server start."""
    try:
        load_index()
        logger.info("pgvector collection initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize pgvector on startup: {e}")


# ---------- Pydantic Models ----------

class ChatRequest(BaseModel):
    query: str

class GeneralRequest(BaseModel):
    query: str


# ---------- Session Helper ----------

def get_session_id(request: Request, response: Response) -> str:
    """Get or create a session ID from the X-Session-ID header."""
    session_id = request.headers.get("x-session-id")
    if not session_id:
        session_id = str(uuid.uuid4())
    response.headers["X-Session-ID"] = session_id
    return session_id


# ---------- Endpoints ----------

@app.post("/upload")
def upload(file: UploadFile):
    try:
        # Validate file extension
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Read file into memory
        contents = file.file.read()
        size_mb = len(contents) / (1024 * 1024)

        if size_mb > MAX_UPLOAD_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large ({size_mb:.1f}MB). Maximum allowed: {MAX_UPLOAD_MB}MB"
            )

        # Ingest PDF (uploads to Supabase Storage, no local disk)
        doc_id = ingest_pdf_bytes(contents, file.filename)

        return {"doc_id": doc_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Upload failed. Please try again.")


@app.post("/chat")
def chat(body: ChatRequest, request: Request, response: Response):
    try:
        session_id = get_session_id(request, response)
        return ask_question(body.query, session_id=session_id)
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process your question.")


@app.get("/documents")
def docs():
    try:
        return get_documents()
    except Exception as e:
        logger.error(f"Documents list error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load documents.")


@app.delete("/documents/{doc_id}")
def delete(doc_id: str):
    try:
        delete_document(doc_id)
        delete_doc(doc_id)
        clear_memory()
        return {"status": "deleted"}
    except Exception as e:
        logger.error(f"Delete error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete document.")


@app.post("/general")
def general(body: GeneralRequest):
    try:
        ans = general_llm_answer(body.query)
        return {"response": ans}
    except Exception as e:
        logger.error(f"General AI error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="General AI failed. Please try again.")


@app.get("/topics")
def topics():
    """Return topic summaries for all uploaded documents."""
    try:
        return {"response": get_all_topics()}
    except Exception as e:
        logger.error(f"Topics error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve topics.")
