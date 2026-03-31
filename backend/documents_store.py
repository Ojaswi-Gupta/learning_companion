"""Document metadata store backed by Supabase Postgres.

Requires a 'documents' table in Supabase:

    CREATE TABLE IF NOT EXISTS documents (
        doc_id   TEXT PRIMARY KEY,
        name     TEXT NOT NULL,
        topics   TEXT
    );
"""

from supabase_client import supabase


def save_document(doc_id, name, topics):
    """Insert or update a document record."""

    supabase.table("documents").upsert({
        "doc_id": doc_id,
        "name": name,
        "topics": topics
    }).execute()


def get_documents():
    """Return all documents as a dict keyed by doc_id."""

    result = supabase.table("documents").select("*").execute()

    docs = {}
    for row in result.data:
        docs[row["doc_id"]] = {
            "name": row["name"],
            "topics": row["topics"]
        }

    return docs


def delete_document(doc_id):
    """Delete a document record by doc_id."""

    supabase.table("documents").delete().eq("doc_id", doc_id).execute()