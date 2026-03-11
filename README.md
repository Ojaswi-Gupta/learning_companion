# AI Learning Companion

An AI-powered document assistant that allows users to upload PDFs and ask questions about them using Retrieval-Augmented Generation (RAG).

## Features

- PDF document upload
- Semantic search using FAISS
- Document-based question answering
- Topic extraction from uploaded documents
- Chat memory for conversations
- General AI fallback when answer is not in documents
- Markdown-rendered responses
- Document management (upload/delete)

## Tech Stack

Backend
- FastAPI
- FAISS vector database
- Sentence Transformers embeddings
- Groq LLM API

Frontend
- HTML
- CSS
- JavaScript
- Marked.js (markdown rendering)

## Architecture

User Question  
↓  
Embedding Generation  
↓  
FAISS Vector Search  
↓  
Context Retrieval  
↓  
LLM Answer Generation  

