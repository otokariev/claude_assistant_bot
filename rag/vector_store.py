import chromadb
from rag.embeddings import get_embedding

# Initialize ChromaDB client with local persistence
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")


def add_document(doc_id: str, text: str, metadata: dict = None):
    """Add a document to the vector store."""
    embedding = get_embedding(text)
    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata or {}]
    )


def search_documents(query: str, n_results: int = 3) -> list[dict]:
    """
    Search for similar documents by query.
    Returns list of dicts with text and metadata.
    """
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    documents = []
    for i, doc in enumerate(results["documents"][0]):
        documents.append({
            "text": doc,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })
    return documents


def delete_document(doc_id: str):
    """Delete a document from the vector store by id."""
    collection.delete(ids=[doc_id])


def get_collection_count() -> int:
    """Get total number of documents in the vector store."""
    return collection.count()