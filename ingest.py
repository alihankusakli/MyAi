import os
import chromadb

chroma = chromadb.PersistentClient(path="./processed")
collection = chroma.get_or_create_collection(name="myai")

def chunk_text(text, chunk_size=150):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def ingest_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    print(f"Ingesting {len(chunks)} chunks from {filepath}...")

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{filepath}_{i}"]
        )

    print("Done.")

if __name__ == "__main__":
    for filename in os.listdir("./data"):
        if filename.endswith(".txt") or filename.endswith(".md"):
            ingest_file(f"./data/{filename}")