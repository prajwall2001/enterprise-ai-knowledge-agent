from app.vector_store import search_chunks

question = "What should happen if a product fails quality inspection?"

results = search_chunks(question, top_k=3)

print("\nQuestion:", question)
print("\nRetrieved results:")

for i, result in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("Source:", result["metadata"]["source"])
    print("Page:", result["metadata"]["page"])
    print("Distance:", result["distance"])
    print("Content:", result["text"])