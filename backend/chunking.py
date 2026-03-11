import re
from typing import List, Dict, Any


def chunk_text(
    text: str,
    doc_id: str,
    file_name: str,
    page_number: int,
    chunk_size: int = 1024,
    overlap: int = 256
) -> List[Dict[str, Any]]:

    chunks = []

    paragraphs = re.split(r'\n\s*\n+', text)

    current_chunk = ""
    start_idx = 0

    for paragraph in paragraphs:

        sentences = re.split(r'(?<=[.!?])\s+', paragraph)

        for sentence in sentences:

            if len(current_chunk) + len(sentence) <= chunk_size:

                current_chunk += (" " if current_chunk else "") + sentence

            else:

                if current_chunk:

                    chunks.append({
                        "text": current_chunk,
                        "doc_id": doc_id,
                        "file_name": file_name,
                        "page": page_number,
                        "start_idx": start_idx,
                        "end_idx": start_idx + len(current_chunk)
                    })

                    start_idx += len(current_chunk) - overlap
                    current_chunk = sentence

                else:

                    words = sentence.split(" ")
                    word_chunk = ""

                    for word in words:

                        if len(word_chunk) + len(word) <= chunk_size:

                            word_chunk += (" " if word_chunk else "") + word

                        else:

                            chunks.append({
                                "text": word_chunk,
                                "doc_id": doc_id,
                                "file_name": file_name,
                                "page": page_number,
                                "start_idx": start_idx,
                                "end_idx": start_idx + len(word_chunk)
                            })

                            start_idx += len(word_chunk) - overlap
                            word_chunk = word

                    current_chunk = word_chunk

    if current_chunk:

        chunks.append({
            "text": current_chunk,
            "doc_id": doc_id,
            "file_name": file_name,
            "page": page_number,
            "start_idx": start_idx,
            "end_idx": start_idx + len(current_chunk)
        })

    return chunks