import streamlit as st
from qa import ask_question, get_vectorstore


def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # stores list of (user, assistant)
    if "book_choice" not in st.session_state:
        st.session_state.book_choice = "All"


def get_books():
    db = get_vectorstore()
    docs = db.similarity_search("probe", k=100)
    titles = sorted({d.metadata.get("book_title", "Unknown") for d in docs})
    return titles


# ----------------------- Streamlit UI -----------------------

st.set_page_config(page_title="Bible & Book Scholar", layout="wide")
st.title("📚 Bible & Book Scholar (Ollama + llama3)")

init_session_state()

# Sidebar filter
st.sidebar.header("Book Filter")

books = ["All"] + get_books()
selected_book = st.sidebar.selectbox("Limit search to a specific book:", books)
st.session_state.book_choice = selected_book

st.sidebar.markdown("---")
st.sidebar.write("Books in your library:")
for b in books[1:]:
    st.sidebar.write(f"- {b}")

st.markdown("Ask questions about the Bible or any loaded book. You can ask unlimited follow-ups.")


# ----------------------- USER INPUT -----------------------

# This is the text box that lets the user submit *multiple* questions
user_question = st.text_input("Your question:", key="question_input")

if st.button("Ask"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            answer, docs = ask_question(
                user_question,
                None if selected_book == "All" else selected_book,
            )

        # Store in chat history
        st.session_state.chat_history.append((user_question, answer))


# ----------------------- DISPLAY CHAT HISTORY -----------------------

st.markdown("## Conversation")

if len(st.session_state.chat_history) == 0:
    st.info("Ask your first question above!")
else:
    for i, (q, a) in enumerate(st.session_state.chat_history, 1):
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Scholar:** {a}")
        st.markdown("---")
