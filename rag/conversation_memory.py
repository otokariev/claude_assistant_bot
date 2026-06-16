import time

import chromadb

from rag.embeddings import get_embedding

chroma_client = chromadb.PersistentClient(path="./chroma_db")
history_collection = chroma_client.get_or_create_collection(name="conversation_history")


def save_message(user_id: int, role: str, text: str, project: str):
    """Save a conversation message to vector store for long-term recall."""
    doc_id = f"msg_{user_id}_{int(time.time() * 1000)}_{role}"
    embedding = get_embedding(text)
    history_collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{
            "user_id": str(user_id),
            "project": project,
            "role": role,
            "timestamp": time.time()
        }]
    )


def search_history(user_id: int, query: str, project: str, n_results: int = 5) -> list[dict]:
    """Search conversation history within a project for messages relevant to the query."""
    query_embedding = get_embedding(query)
    results = history_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"$and": [{"user_id": str(user_id)}, {"project": project}]}
    )

    messages = []
    for i, doc in enumerate(results["documents"][0]):
        messages.append({
            "text": doc,
            "role": results["metadatas"][0][i]["role"],
        })
    return messages


def get_all_messages(user_id: int, project: str) -> list[dict]:
    """Get all messages for a user's project, sorted by time. Used for export."""
    results = history_collection.get(
        where={"$and": [{"user_id": str(user_id)}, {"project": project}]}
    )

    messages = []
    for i, doc in enumerate(results["documents"]):
        messages.append({
            "text": doc,
            "role": results["metadatas"][i]["role"],
            "timestamp": results["metadatas"][i]["timestamp"]
        })

    messages.sort(key=lambda m: m["timestamp"])
    return messages


def delete_project_history(user_id: int, project: str):
    """Delete all messages for a specific project from vector store."""
    history_collection.delete(
        where={"$and": [{"user_id": str(user_id)}, {"project": project}]}
    )