
import requests
from app.vector_store import search_chunks

question = "What should happen if a product fails quality inspection?"

# 1. Retrieve relevant document chunks
results = search_chunks(question, top_k=3)

# 2. Build context from retrieved documents
context = "\n\n".join(result["text"] for result in results)

# 3. Create a prompt with context and question
prompt = f"""
You are an AI knowledge assistant.
Answer the question using only the provided context.
If the answer is not present in the context, say you don't know.

Context:
{context}

Question:
{question}

Answer:
"""

# 4. Send prompt to Ollama (local LLM)
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:0.5b",
        "prompt": prompt,
        "stream": False
    },
    timeout=120
)

# 5. Display the AI answer
response.raise_for_status()
answer = response.json()["response"]

print("\nQuestion:", question)
print("\nAI Answer:\n")
print(answer)
