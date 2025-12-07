import streamlit as st
from qa import ask_question, get_available_traditions
from config import TRADITIONS, ADVISOR_NAME, ADVISOR_GREETING

# ----------------------- Page Configuration -----------------------
st.set_page_config(
    page_title="Divine Wisdom Guide",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------- Custom Styling -----------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');
    
    /* Main background with subtle gradient */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
    }
    
    /* Header styling */
    .main-header {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3rem;
        font-weight: 600;
        text-align: center;
        background: linear-gradient(90deg, #ffd700, #fff8dc, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
    }
    
    .sub-header {
        font-family: 'Lora', serif;
        font-size: 1.1rem;
        text-align: center;
        color: #b8b8d1;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    /* Greeting card */
    .greeting-card {
        background: linear-gradient(145deg, rgba(255,215,0,0.1), rgba(255,248,220,0.05));
        border: 1px solid rgba(255,215,0,0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0 2rem 0;
        font-family: 'Lora', serif;
        color: #e8e8f0;
        line-height: 1.8;
    }
    
    /* Chat messages */
    .seeker-message {
        background: linear-gradient(135deg, rgba(70, 130, 180, 0.2), rgba(100, 149, 237, 0.1));
        border-left: 3px solid #6495ed;
        border-radius: 0 15px 15px 0;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        font-family: 'Lora', serif;
        color: #e8e8f0;
    }
    
    .advisor-message {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(218, 165, 32, 0.05));
        border-left: 3px solid #ffd700;
        border-radius: 0 15px 15px 0;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Lora', serif;
        color: #f0f0f5;
        line-height: 1.9;
    }
    
    .message-label {
        font-family: 'Cormorant Garamond', serif;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .seeker-label {
        color: #6495ed;
    }
    
    .advisor-label {
        color: #ffd700;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e3f 0%, #0f0f23 100%);
    }
    
    .tradition-header {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.5rem;
        color: #ffd700;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .tradition-item {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255,215,0,0.1);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,215,0,0.3);
        border-radius: 10px;
        color: #f0f0f5;
        font-family: 'Lora', serif;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ffd700, #daa520);
        color: #1a1a2e;
        font-family: 'Cormorant Garamond', serif;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #fff8dc, #ffd700);
        box-shadow: 0 5px 20px rgba(255,215,0,0.4);
        transform: translateY(-2px);
    }
    
    /* Divider */
    .sacred-divider {
        text-align: center;
        color: rgba(255,215,0,0.5);
        margin: 2rem 0;
        font-size: 1.5rem;
        letter-spacing: 1rem;
    }
    
    /* Sources panel */
    .sources-panel {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid rgba(255,215,0,0.1);
    }
    
    .source-item {
        font-family: 'Lora', serif;
        font-size: 0.85rem;
        color: #a0a0b8;
        padding: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Multiselect styling */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: rgba(255,215,0,0.2);
    }
</style>
""", unsafe_allow_html=True)


# ----------------------- Session State -----------------------
def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_traditions" not in st.session_state:
        st.session_state.selected_traditions = []
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = False


init_session_state()


# ----------------------- Sidebar -----------------------
with st.sidebar:
    st.markdown('<div class="tradition-header">🕊️ Sacred Traditions</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <p style="color: #b8b8d1; font-family: 'Lora', serif; font-size: 0.9rem; text-align: center;">
    Select which wisdom traditions to draw guidance from
    </p>
    """, unsafe_allow_html=True)
    
    # Get available traditions
    available = get_available_traditions()
    
    # Multi-select for traditions
    selected = st.multiselect(
        "Choose traditions:",
        options=["All Traditions"] + list(TRADITIONS.keys()),
        default=["All Traditions"],
        help="Select one or more traditions, or 'All' for universal wisdom"
    )
    st.session_state.selected_traditions = selected
    
    st.markdown("---")
    
    # Display tradition info
    st.markdown("### 📜 Available Scriptures")
    
    for tradition, info in TRADITIONS.items():
        with st.expander(f"{info['icon']} {tradition}"):
            st.markdown(f"*{info['description']}*")
            st.markdown("**Texts:**")
            for scripture in info['scriptures']:
                st.markdown(f"- {scripture.replace('.txt', '').replace('_', ' ').title()}")
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    st.session_state.show_sources = st.checkbox(
        "Show scripture sources",
        value=st.session_state.show_sources,
        help="Display the specific passages used for guidance"
    )
    
    if st.button("🔄 Clear Conversation"):
        st.session_state.chat_history = []
        st.rerun()


# ----------------------- Main Content -----------------------

# Header
st.markdown('<h1 class="main-header">🕊️ Divine Wisdom Guide</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Seek guidance from the sacred wisdom of humanity\'s spiritual traditions</p>', 
    unsafe_allow_html=True
)

# Greeting (show only when no conversation)
if len(st.session_state.chat_history) == 0:
    st.markdown(f"""
    <div class="greeting-card">
        <em>{ADVISOR_GREETING}</em>
        <br><br>
        You may ask about:
        <ul>
            <li>Life decisions and moral dilemmas</li>
            <li>Relationships and forgiveness</li>
            <li>Finding purpose and meaning</li>
            <li>Dealing with suffering and grief</li>
            <li>Cultivating peace and wisdom</li>
            <li>Any matter that weighs upon your heart</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Conversation display
if len(st.session_state.chat_history) > 0:
    for i, (question, answer, sources) in enumerate(st.session_state.chat_history):
        # Seeker's message
        st.markdown(f"""
        <div class="seeker-message">
            <div class="message-label seeker-label">🙏 You Asked</div>
            {question}
        </div>
        """, unsafe_allow_html=True)
        
        # Advisor's response
        st.markdown(f"""
        <div class="advisor-message">
            <div class="message-label advisor-label">✨ Divine Wisdom</div>
            {answer}
        </div>
        """, unsafe_allow_html=True)
        
        # Sources (if enabled)
        if st.session_state.show_sources and sources:
            with st.expander(f"📖 Scripture Sources ({len(sources)} passages)"):
                for j, doc in enumerate(sources, 1):
                    tradition = doc.metadata.get('tradition', 'Unknown')
                    scripture = doc.metadata.get('scripture_name', doc.metadata.get('book_title', 'Unknown'))
                    st.markdown(f"**[{j}] {tradition} - {scripture}**")
                    st.markdown(f"> {doc.page_content[:300]}...")
                    st.markdown("---")
    
    st.markdown('<div class="sacred-divider">✦ ✦ ✦</div>', unsafe_allow_html=True)


# ----------------------- Input Area -----------------------
st.markdown("### 💭 Share Your Question")

col1, col2 = st.columns([5, 1])

with col1:
    user_question = st.text_area(
        "What guidance do you seek?",
        placeholder="Share what's on your mind or ask for guidance on any matter...",
        height=100,
        label_visibility="collapsed"
    )

with col2:
    st.write("")  # Spacer
    ask_button = st.button("🙏 Seek Wisdom", use_container_width=True)

# Process question
if ask_button:
    if user_question.strip() == "":
        st.warning("Please share your question or concern.")
    else:
        with st.spinner("🕊️ Contemplating the sacred texts..."):
            # Get traditions filter
            traditions_filter = None
            if st.session_state.selected_traditions:
                if "All Traditions" not in st.session_state.selected_traditions:
                    traditions_filter = st.session_state.selected_traditions
            
            # Get conversation history for context
            history = [(q, a) for q, a, _ in st.session_state.chat_history]
            
            # Ask the question
            answer, docs = ask_question(
                user_question,
                traditions=traditions_filter,
                conversation_history=history
            )

        # Store in chat history
            st.session_state.chat_history.append((user_question, answer, docs))
            
            # Refresh to show new message
            st.rerun()


# ----------------------- Footer -----------------------
        st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-family: 'Lora', serif; font-size: 0.85rem;">
    <em>"The beginning of wisdom is the definition of terms."</em> — Socrates
    <br><br>
    This advisor draws upon sacred texts to offer guidance. 
    For matters of health, legal issues, or emergencies, please consult appropriate professionals.
</div>
""", unsafe_allow_html=True)
