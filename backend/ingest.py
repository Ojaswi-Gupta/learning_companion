from pypdf import PdfReader
import uuid
import os
import tempfile

from embeddings import embed_texts
from vector_store import add_documents
from documents_store import save_document
from rag_pipeline import extract_topics
from chunking import chunk_text
from supabase_client import supabase


def upload_to_storage(file_bytes, file_name):
    """Upload file bytes to Supabase Storage and return the storage path."""

    storage_path = f"{uuid.uuid4().hex[:8]}_{file_name}"

    supabase.storage.from_("uploads").upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": "application/pdf"}
    )

    return storage_path


def delete_from_storage(storage_path):
    """Delete a file from Supabase Storage."""

    try:
        supabase.storage.from_("uploads").remove([storage_path])
    except Exception:
        pass  # Non-critical if storage cleanup fails


def ingest_pdf_bytes(file_bytes, original_name):
    """Ingest a PDF from raw bytes (no local disk storage).

    Args:
        file_bytes: the raw PDF file content
        original_name: original filename for display

    Returns:
        doc_id: the generated document ID
    """

    # Upload to Supabase Storage (cloud)
    storage_path = upload_to_storage(file_bytes, original_name)

    # Write to a temp file for PyPDF to read (cleaned up automatically)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
        tmp.write(file_bytes)
        tmp.flush()

        reader = PdfReader(tmp.name)

        doc_id = str(uuid.uuid4())
        file_name = original_name

        full_text = ""
        texts = []

        for i, page in enumerate(reader.pages):
            t = page.extract_text()
            if not t:
                continue

            full_text += t

            chunks = chunk_text(
                text=t,
                doc_id=doc_id,
                file_name=file_name,
                page_number=i
            )

            texts.extend(chunks)

    # Generate embeddings and store in pgvector
    vectors = embed_texts([t["text"] for t in texts])
    add_documents(texts, vectors)

    # Extract topics and save document metadata
    topics = extract_topics(full_text)
    save_document(doc_id, file_name, topics)

    return doc_id