from fastapi import FastAPI,UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

from ingest import ingest_pdf
from rag_pipeline import ask_question,clear_memory,general_llm_answer
from vector_store import load_index,delete_doc
from documents_store import get_documents,delete_document


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

os.makedirs("data/uploads",exist_ok=True)

load_index()

@app.post("/upload")
async def upload(file:UploadFile):

    path=f"data/uploads/{file.filename}"

    with open(path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)

    doc_id=ingest_pdf(path)

    return {"doc_id":doc_id}


@app.post("/chat")
async def chat(query:str):
    return ask_question(query)


@app.get("/documents")
def docs():

    return get_documents()


@app.delete("/documents/{doc_id}")
def delete(doc_id:str):

    delete_document(doc_id)

    delete_doc(doc_id)

    clear_memory()

    return {"status":"deleted"}

@app.post("/general")
async def general(query:str):

    ans=general_llm_answer(query)

    return {"response":ans}
