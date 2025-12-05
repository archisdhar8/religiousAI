import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Use llama3 in Ollama
OLLAMA_MODEL = "llama3"
