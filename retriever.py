import chromadb

chroma = chromadb.PersistentClient(path="./processed")
collection = chroma.get_or_create_collection(name="myai")

def retrieve(query, n_results=3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results["documents"][0]

if __name__ == "__main__":
    query = input("Test query: ")
    chunks = retrieve(query)
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---\n{chunk}")