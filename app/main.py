
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.ingestion.pdf_loader import extract_pdf_pages
from app.ingestion.chunker import split_into_chunks
from app.vector_store import store_chunks, search_chunks, collection

app = FastAPI(
    title="Enterprise AI Knowledge Agent",
    description="Document-based RAG application",
    version="0.3.0"
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Enterprise AI Knowledge Agent is running!"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "stored_chunks": collection.count()
    }


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded PDF is empty.")

    if len(pdf_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Maximum PDF size is 10 MB.")

    try:
        pages = extract_pdf_pages(pdf_bytes)
        chunks = split_into_chunks(pages, chunk_size=500, overlap=100)

        stored_count = store_chunks(chunks, source=file.filename)

        return {
            "filename": file.filename,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "stored_chunks": stored_count,
            "message": "PDF processed and stored successfully"
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        print(f"Document processing error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process and store this PDF."
        )

    finally:
        await file.close()


@app.post("/chat")
def chat(request: ChatRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # 1. Retrieve relevant document chunks
    results = search_chunks(question, top_k=3)

    if not results:
        return {
            "question": question,
            "answer": "No documents have been uploaded yet.",
            "sources": []
        }

    # 2. Build context from retrieved documents
    context = "\n\n".join(result["text"] for result in results)

    # 3. Build the RAG prompt
    prompt = f"""
You are an AI knowledge assistant.
Answer the question using only the provided context.
If the answer is not present in the context, say you don't know.
Do not make up information.

Context:
{context}

Question:
{question}

Answer:
"""

    # 4. Send prompt to Ollama
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:0.5b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()
        answer = response.json()["response"].strip()

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Ollama is not running. Please start Ollama."
        )

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="The AI model took too long to respond."
        )

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to get a response from Ollama."
        )

    # 5. Return answer and document sources
    sources = [
        {
            "source": result["metadata"]["source"],
            "page": result["metadata"]["page"],
            "distance": result["distance"]
        }
        for result in results
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }
