from pypdf import PdfReader
import uuid
import os

from embeddings import embed_texts
from vector_store import add_documents
from documents_store import save_document
from rag_pipeline import extract_topics


def chunk(text, size=500, overlap=100):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        part = " ".join(words[start:start + size])

        chunks.append(part)

        start += size - overlap

    return chunks


def ingest_pdf(path):

    reader = PdfReader(path)

    doc_id = str(uuid.uuid4())

    file_name = os.path.basename(path)

    full_text = ""

    texts = []

    for i, page in enumerate(reader.pages):

        t = page.extract_text()

        if not t:
            continue

        full_text += t

        chunks = chunk(t)

        for c in chunks:

            texts.append({
                "text": c,
                "doc_id": doc_id,
                "file_name": file_name,
                "page": i
            })

    vectors = embed_texts([t["text"] for t in texts])

    add_documents(texts, vectors)

    topics = extract_topics(full_text)

    save_document(doc_id, file_name, topics)

    return doc_id