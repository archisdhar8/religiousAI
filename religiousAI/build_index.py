import os
from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config import RAW_DATA_DIR, VECTORSTORE_DIR, EMBEDDING_MODEL_NAME


def load_books() -> List:
    docs = []
    for filename in os.listdir(RAW_DATA_DIR):
        if filename.lower().endswith(".txt"):
            path = os.path.join(RAW_DATA_DIR, filename)
            loader = TextLoader(path, encoding="utf-8")
            book_docs = loader.load()

            book_title = filename.replace(".txt", "")

            # Add metadata
            for d in book_docs:
                d.metadata["book_title"] = book_title
                d.metadata["source_file"] = filename

            docs.extend(book_docs)
    return docs


def chunk_documents(docs: List):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        length_function=len,
    )
    return splitter.split_documents(docs)


def build_vectorstore():
    print("Loading books...")
    docs = load_books()
    print(f"Loaded {len(docs)} documents")

    print("Chunking...")
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")

    print("Embedding...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    print("Creating vectorstore...")
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR,
    )

    print("Done! Vectorstore saved to:", VECTORSTORE_DIR)


if __name__ == "__main__":
    build_vectorstore()
