from embeddings import embed_query
from vector_store import search
from documents_store import get_documents
from config import GROQ_API_KEY, LLM_MODEL
from groq import Groq

client = Groq(api_key=GROQ_API_KEY)

chat_memory = []


def clear_memory():
    global chat_memory
    chat_memory = []


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


def ask_question(query):

    global chat_memory

    q = query.lower()

    if "topic" in q or "topics" in q:

        docs = get_documents()

        if not docs:
            return {"response": "No documents uploaded.", "fallback": False}

        out = ""

        for d in docs.values():
            out += f"{d['name']}:\n{d['topics']}\n\n"

        return {"response": out, "fallback": False}

    vec = embed_query(query)

    docs = search(vec, 10)

    docs=[d for d in docs if d["score"] < 1.0]

    if not docs:

        return {
            "response": "The uploaded documents do not contain this information.",
            "fallback": True
        }

    context = "\n\n".join([d["text"] for d in docs])

    history = ""

    for m in chat_memory[-5:]:
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

    chat_memory.append({"role": "user", "content": query})
    chat_memory.append({"role": "assistant", "content": answer})

    return {"response": answer, "fallback": False}