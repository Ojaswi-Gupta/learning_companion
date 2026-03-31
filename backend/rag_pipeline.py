from embeddings import embed_query
from vector_store import search
from documents_store import get_documents
from config import GROQ_API_KEY, LLM_MODEL, SCORE_THRESHOLD
from groq import Groq

client = Groq(api_key=GROQ_API_KEY)


class ChatMemoryManager:
    """Manages per-session conversation history."""

    def __init__(self, max_history=5):
        self._sessions = {}
        self._max_history = max_history

    def get(self, session_id):
        """Return the chat history for a session."""
        return self._sessions.get(session_id, [])

    def append(self, session_id, role, content):
        """Add a message to a session's history."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({"role": role, "content": content})
        # Keep only the last N exchanges
        self._sessions[session_id] = self._sessions[session_id][-(self._max_history * 2):]

    def clear(self, session_id=None):
        """Clear one session or all sessions."""
        if session_id:
            self._sessions.pop(session_id, None)
        else:
            self._sessions.clear()


memory_manager = ChatMemoryManager()


def clear_memory(session_id=None):
    memory_manager.clear(session_id)


def extract_topics(text):

    prompt = f"""
Extract the main topics covered in this document.

{text[:5000]}
"""

    r = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return r.choices[0].message.content.strip()


def general_llm_answer(query):

    r = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": query}]
    )

    return r.choices[0].message.content.strip()


def get_all_topics():
    """Return topic summaries for all uploaded documents."""

    docs = get_documents()

    if not docs:
        return "No documents uploaded."

    out = ""
    for d in docs.values():
        out += f"{d['name']}:\n{d['topics']}\n\n"

    return out.strip()


def ask_question(query, session_id="default"):

    vec = embed_query(query)

    docs = search(vec, 10)

    docs = [d for d in docs if d["score"] < SCORE_THRESHOLD]

    if not docs:
        return {
            "response": "The uploaded documents do not contain this information.",
            "fallback": True
        }

    context = "\n\n".join([d["text"] for d in docs])

    history = ""
    for m in memory_manager.get(session_id):
        history += f"{m['role']}: {m['content']}\n"

    prompt = f"""
You are an AI assistant answering questions from uploaded documents.

Rules:
- Use ONLY the provided context.
- If the context does not contain the answer say:
  "The uploaded documents do not contain this information."
- Do NOT use markdown symbols such as **, *, or _.
- Do NOT format text using markdown.
- If emphasis is needed, write normally instead of using markdown formatting.

Conversation History:
{history}

Context:
{context}

Question:
{query}

Provide a clear and concise answer in normal readable text.
"""

    r = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = r.choices[0].message.content.strip()

    memory_manager.append(session_id, "user", query)
    memory_manager.append(session_id, "assistant", answer)

    needs_fallback = "do not contain this information" in answer.lower()

    return {"response": answer, "fallback": needs_fallback}