import json
import os
from config import DOC_STORE


def load_store():

    if not os.path.exists(DOC_STORE):
        return {}

    with open(DOC_STORE, "r") as f:
        return json.load(f)


def save_store(data):

    with open(DOC_STORE, "w") as f:
        json.dump(data, f, indent=2)


def save_document(doc_id, name, topics):

    data = load_store()

    data[doc_id] = {
        "name": name,
        "topics": topics
    }

    save_store(data)


def get_documents():
    return load_store()


def delete_document(doc_id):

    data = load_store()

    if doc_id in data:
        del data[doc_id]

    save_store(data)