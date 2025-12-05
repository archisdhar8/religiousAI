from typing import List, Optional, Tuple

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama

from langchain_core.messages import SystemMessage, HumanMessage

from config import VECTORSTORE_DIR, EMBEDDING_MODEL_NAME, OLLAMA_MODEL


def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings,
    )


def retrieve(question: str, book_title: Optional[str], k: int = 6):
    db = get_vectorstore()

    if book_title and book_title.lower() != "all":
        return db.similarity_search(question, k=k, filter={"book_title": book_title})

    return db.similarity_search(question, k=k)


def context_to_text(docs):
    blocks = []
    for i, d in enumerate(docs, 1):
        blocks.append(
            f"[{i}] Book: {d.metadata.get('book_title')} | Source: {d.metadata.get('source_file')}\n"
            f"{d.page_content.strip()}"
        )
    return "\n\n".join(blocks)


def ask_question(question: str, book_title: Optional[str] = None):
    docs = retrieve(question, book_title)
    context = context_to_text(docs)

    system_prompt = (
        "You are a scholarly expert who answers only using the provided context. "
        "If the answer cannot be found in the context, say 'Not enough information in the text.' "
        "Always cite which book or passage your answer is based on."
    )

    user_prompt = (
        f"Question:\n{question}\n\n"
        f"Context:\n{context}\n\n"
        "Answer using ONLY the context."
    )

    llm = Ollama(model=OLLAMA_MODEL)

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    return response, docs
