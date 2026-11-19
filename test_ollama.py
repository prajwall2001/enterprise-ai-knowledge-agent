
import requests

url = "http://localhost:11434/api/generate"

context = """
RAG stands for Retrieval-Augmented Generation.

Retrieval:
The system searches external documents for relevant information.

Augmentation:
The retrieved information is added to the user's question
as additional context.

Generation:
The language model uses the question and retrieved context
to generate an answer.
"""

question = "Explain the three stages of RAG."

prompt = f"""
Answer the question using ONLY the information below.

CONTEXT:
{context}

QUESTION:
{question}

Give a simple explanation in three numbered points.
Do not introduce information that is not in the context.
"""

payload = {
    "model": "qwen2.5:0.5b",
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.1
    }
}

response = requests.post(
    url,
    json=payload,
    timeout=120
)

response.raise_for_status()

result = response.json()

print("\nQUESTION:", question)
print("\nAI RESPONSE:\n")
print(result["response"])
