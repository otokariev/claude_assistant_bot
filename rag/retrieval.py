from rag.vector_store import search_documents
from claude.client import ask_claude
from bot.config import CLAUDE_SONNET


def answer_with_rag(question: str) -> str:
    """
    Answer a question using RAG pipeline.
    1. Search for relevant documents
    2. Build context from results
    3. Ask Claude with context
    """
    # Step 1 - find relevant documents
    relevant_docs = search_documents(question, n_results=3)

    if not relevant_docs:
        return "No documents found. Please upload documents first using /upload command."

    # Step 2 - build context from found documents
    context = "\n\n---\n\n".join([doc["text"] for doc in relevant_docs])

    # Step 3 - ask Claude with context
    system_prompt = """
    You are a helpful assistant that answers questions based on provided documents.
    Answer only based on the context provided. 
    If the answer is not in the context, say so clearly.
    Be concise and accurate.
    """

    messages = [
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        }
    ]

    return ask_claude(messages=messages, system=system_prompt, model=CLAUDE_SONNET)