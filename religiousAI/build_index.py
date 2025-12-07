import os
import re
import shutil
from typing import List, Dict, Optional

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config import RAW_DATA_DIR, VECTORSTORE_DIR, EMBEDDING_MODEL_NAME, TRADITIONS


def get_tradition_for_file(filename: str) -> Optional[Dict]:
    """
    Determine which tradition a scripture file belongs to.
    Returns tradition name and metadata, or None if not matched.
    """
    filename_lower = filename.lower()
    
    for tradition_name, info in TRADITIONS.items():
        for scripture in info['scriptures']:
            # Match by exact name or similar pattern
            if scripture.lower() in filename_lower or filename_lower in scripture.lower():
                return {
                    'tradition': tradition_name,
                    'icon': info['icon'],
                    'scripture_name': scripture.replace('.txt', '').replace('_', ' ').title()
                }
    
    # Try to infer from filename patterns
    patterns = {
        'bible': ('Christianity', '✝️', 'Bible'),
        'quran': ('Islam', '☪️', 'Quran'),
        'koran': ('Islam', '☪️', 'Quran'),
        'gita': ('Hinduism', '🕉️', 'Bhagavad Gita'),
        'upanishad': ('Hinduism', '🕉️', 'Upanishads'),
        'veda': ('Hinduism', '🕉️', 'Vedas'),
        'dhamma': ('Buddhism', '☸️', 'Dhammapada'),
        'sutra': ('Buddhism', '☸️', 'Sutras'),
        'buddha': ('Buddhism', '☸️', 'Buddhist Texts'),
        'tao': ('Taoism', '☯️', 'Tao Te Ching'),
        'torah': ('Judaism', '✡️', 'Torah'),
        'talmud': ('Judaism', '✡️', 'Talmud'),
        'guru': ('Sikhism', '🙏', 'Guru Granth Sahib'),
        'granth': ('Sikhism', '🙏', 'Guru Granth Sahib'),
    }
    
    for pattern, (tradition, icon, name) in patterns.items():
        if pattern in filename_lower:
            return {
                'tradition': tradition,
                'icon': icon,
                'scripture_name': name
            }
    
    # Default fallback
    return {
        'tradition': 'Other',
        'icon': '📖',
        'scripture_name': filename.replace('.txt', '').replace('_', ' ').title()
    }


def clean_text(text: str) -> str:
    """Clean and normalize scripture text."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove leading/trailing whitespace from lines
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    return text


def load_scriptures() -> List:
    """
    Load all scripture files from the raw data directory.
    Adds rich metadata including tradition, scripture name, etc.
    """
    docs = []
    
    if not os.path.exists(RAW_DATA_DIR):
        print(f"Warning: Data directory not found: {RAW_DATA_DIR}")
        print("Please add scripture text files to this directory.")
        return docs
    
    files = [f for f in os.listdir(RAW_DATA_DIR) if f.lower().endswith('.txt')]
    
    if not files:
        print(f"No .txt files found in {RAW_DATA_DIR}")
        return docs
    
    for filename in files:
        path = os.path.join(RAW_DATA_DIR, filename)
        print(f"  Loading: {filename}")
        
        try:
            loader = TextLoader(path, encoding="utf-8")
            file_docs = loader.load()
        except Exception as e:
            print(f"  Error loading {filename}: {e}")
            # Try with different encoding
            try:
                loader = TextLoader(path, encoding="latin-1")
                file_docs = loader.load()
            except Exception as e2:
                print(f"  Failed with latin-1 too: {e2}")
                continue
        
        # Get tradition metadata
        tradition_info = get_tradition_for_file(filename)
        
        # Clean text and add metadata
        for d in file_docs:
            d.page_content = clean_text(d.page_content)
            d.metadata.update({
                'tradition': tradition_info['tradition'],
                'icon': tradition_info['icon'],
                'scripture_name': tradition_info['scripture_name'],
                'source_file': filename,
                'book_title': tradition_info['scripture_name']  # For backwards compatibility
            })
        
        docs.extend(file_docs)
        print(f"    ✓ {tradition_info['icon']} {tradition_info['tradition']} - {tradition_info['scripture_name']}")
    
    return docs


def chunk_documents(docs: List, chunk_size: int = 800, chunk_overlap: int = 150):
    """
    Split documents into chunks suitable for embedding.
    Preserves metadata through the splitting process.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_documents(docs)


def build_vectorstore(clear_existing: bool = True):
    """
    Build the vector store from all scripture files.
    
    Args:
        clear_existing: If True, delete existing vectorstore before building
    """
    print("=" * 60)
    print("🕊️  DIVINE WISDOM GUIDE - Building Scripture Index")
    print("=" * 60)
    
    # Optionally clear existing vectorstore
    if clear_existing and os.path.exists(VECTORSTORE_DIR):
        print("\n🗑️  Clearing existing vectorstore...")
        shutil.rmtree(VECTORSTORE_DIR)
    
    print("\n📚 Loading scriptures...")
    docs = load_scriptures()
    
    if not docs:
        print("\n❌ No documents loaded. Please add scripture files to:")
        print(f"   {RAW_DATA_DIR}")
        return
    
    print(f"\n✓ Loaded {len(docs)} documents")
    
    print("\n✂️  Chunking documents...")
    chunks = chunk_documents(docs)
    print(f"✓ Created {len(chunks)} chunks")
    
    # Show tradition breakdown
    tradition_counts = {}
    for chunk in chunks:
        tradition = chunk.metadata.get('tradition', 'Unknown')
        tradition_counts[tradition] = tradition_counts.get(tradition, 0) + 1
    
    print("\n📊 Chunks by tradition:")
    for tradition, count in sorted(tradition_counts.items()):
        icon = next(
            (info['icon'] for t, info in TRADITIONS.items() if t == tradition),
            '📖'
        )
        print(f"   {icon} {tradition}: {count} chunks")
    
    print("\n🔮 Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    print("💾 Building vectorstore...")
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR,
    )
    
    print("\n" + "=" * 60)
    print("✨ SUCCESS! Vectorstore created at:")
    print(f"   {VECTORSTORE_DIR}")
    print("=" * 60)
    print("\nYou can now run: streamlit run app.py")


if __name__ == "__main__":
    import sys
    
    # Check for --no-clear flag
    clear = "--no-clear" not in sys.argv
    
    build_vectorstore(clear_existing=clear)
