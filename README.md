# 🕊️ Divine Wisdom Guide

A spiritual advisor powered by AI that draws upon the sacred wisdom of humanity's great religious and philosophical traditions to provide guidance for life's questions.

![Divine Wisdom Guide](https://img.shields.io/badge/Spiritual-Advisor-gold?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=for-the-badge)

## ✨ Features

- **Multi-Tradition Wisdom**: Draws from Christianity, Islam, Hinduism, Buddhism, Taoism, Judaism, and more
- **Life Guidance**: Not just Q&A - provides thoughtful advice for real-life situations
- **Empathetic Responses**: Responds with compassion, understanding, and wisdom
- **Scripture Sources**: Optionally view the specific passages informing the guidance
- **Beautiful UI**: Immersive, calming interface designed for contemplation
- **Local LLM**: Uses Ollama for privacy - your conversations stay on your machine

## 📚 Supported Scriptures

| Tradition | Texts |
|-----------|-------|
| ✝️ **Christianity** | Bible (KJV, ASV) |
| ☪️ **Islam** | Quran (Shakir translation) |
| 🕉️ **Hinduism** | Bhagavad Gita, Upanishads, Ramayana |
| ☸️ **Buddhism** | Dhammapada, Buddhist Sutras |
| ☯️ **Taoism** | Tao Te Ching |
| ✡️ **Judaism** | Torah, Talmud selections |
| 📜 **Confucianism** | Analects of Confucius |
| 🔥 **Zoroastrianism** | Zend-Avesta |
| 🏛️ **Ancient Wisdom** | Meditations (Marcus Aurelius), Enchiridion (Epictetus) |

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+**
2. **Ollama** with llama3 model:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3
   ```

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/religiousAI.git
cd religiousAI/religiousAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Download Scriptures

```bash
# Download all available scriptures (public domain texts)
python download_scriptures.py --all

# Or download specific traditions:
python download_scriptures.py --tradition buddhism
python download_scriptures.py --tradition hinduism

# List available scriptures:
python download_scriptures.py --list
```

### Build the Index

```bash
python build_index.py
```

### Run the App

```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

## 💭 Example Questions

The Divine Wisdom Guide is designed for life guidance, not just scripture Q&A:

- *"I'm struggling with forgiveness after being betrayed by a close friend"*
- *"How do I find purpose when I feel lost in my career?"*
- *"I'm dealing with grief after losing someone close to me"*
- *"How should I approach a difficult decision about my future?"*
- *"I want to cultivate more patience and inner peace"*
- *"What wisdom can help me be a better parent?"*

## 🛠️ Project Structure

```
religiousAI/
├── app.py                 # Streamlit UI
├── qa.py                  # Core Q&A and advisor logic
├── build_index.py         # Vector store builder
├── config.py              # Configuration and traditions
├── download_scriptures.py # Scripture downloader
├── requirements.txt       # Python dependencies
├── data/
│   └── raw/               # Scripture text files
└── vectorstore/           # ChromaDB vector database
```

## ⚙️ Configuration

Edit `config.py` to customize:

- `OLLAMA_MODEL`: Change the LLM (default: llama3)
- `EMBEDDING_MODEL_NAME`: Change the embedding model
- `TRADITIONS`: Add or modify religious traditions
- `ADVISOR_NAME`: Customize the advisor's name
- `ADVISOR_GREETING`: Customize the welcome message

## 🔧 Adding Custom Scriptures

1. Add `.txt` files to `data/raw/`
2. The filename determines the tradition (e.g., `quran.txt` → Islam)
3. Run `python build_index.py` to rebuild the index

## 🙏 Philosophy

This project is built with deep respect for all religious and spiritual traditions. The AI advisor:

- Never claims divine authority
- Presents wisdom from texts without imposing beliefs
- Acknowledges the limits of AI in matters of the sacred
- Encourages seeking human spiritual guidance for serious matters
- Treats all traditions with equal respect

## 📝 License

MIT License - See LICENSE file for details.

All scripture texts are from public domain sources (primarily Project Gutenberg).

## 🤝 Contributing

Contributions welcome! Please ensure any added scriptures are in the public domain.

---

*"The beginning of wisdom is the definition of terms."* — Socrates
