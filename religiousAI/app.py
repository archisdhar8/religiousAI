"""
Divine Wisdom Guide - Spiritual Advisor Application

A deeply immersive spiritual guidance experience drawing from
humanity's great religious and philosophical traditions.
"""

import streamlit as st
import uuid
import tempfile
import subprocess
import os
import platform
from datetime import datetime

from qa import (
    ask_question, 
    get_available_traditions, 
    compare_traditions,
    generate_daily_wisdom,
    generate_journal_reflection
)
from memory import (
    get_user_id, 
    load_user_memory, 
    save_user_memory,
    add_exchange,
    add_journal_entry,
    get_returning_user_greeting
)
from config import (
    TRADITIONS, 
    ADVISOR_NAME, 
    ADVISOR_GREETING,
    UI_MODES,
    VOICE_ENABLED
)

# Check for TTS availability - macOS has built-in 'say' command
TTS_AVAILABLE = False
TTS_METHOD = None

# Check macOS built-in TTS first (most reliable)
if platform.system() == "Darwin":
    try:
        result = subprocess.run(['which', 'say'], capture_output=True, text=True)
        if result.returncode == 0:
            TTS_AVAILABLE = True
            TTS_METHOD = "macos_say"
    except:
        pass

# Fallback to pyttsx3 if available
if not TTS_AVAILABLE:
    try:
        import pyttsx3
        TTS_AVAILABLE = True
        TTS_METHOD = "pyttsx3"
    except ImportError:
        pass

# =====================================================================
# PAGE CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="Divine Wisdom Guide",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# CUSTOM STYLING
# =====================================================================
def get_custom_css(mode: str = "standard") -> str:
    """Generate CSS based on current mode."""
    
    base_css = """
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #0f0f1f 100%);
    }
    
    /* Typography */
    .main-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3.2rem;
        font-weight: 500;
        text-align: center;
        background: linear-gradient(90deg, #ffd700, #fff8dc, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        letter-spacing: 2px;
    }
    
    .sub-title {
        font-family: 'Crimson Pro', serif;
        font-size: 1.15rem;
        text-align: center;
        color: #9090a8;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    /* Cards and containers */
    .wisdom-card {
        background: linear-gradient(145deg, rgba(255,215,0,0.08), rgba(255,248,220,0.03));
        border: 1px solid rgba(255,215,0,0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        font-family: 'Crimson Pro', serif;
        color: #e8e8f0;
        line-height: 1.9;
    }
    
    .daily-wisdom {
        background: radial-gradient(ellipse at top, rgba(255,215,0,0.15), transparent),
                    linear-gradient(145deg, rgba(30,30,60,0.9), rgba(15,15,35,0.95));
        border: 1px solid rgba(255,215,0,0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0 2rem 0;
        text-align: center;
    }
    
    .daily-wisdom-text {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.4rem;
        font-style: italic;
        color: #f0f0f5;
        line-height: 1.8;
    }
    
    .daily-wisdom-source {
        font-family: 'Crimson Pro', serif;
        font-size: 0.95rem;
        color: #ffd700;
        margin-top: 1rem;
    }
    
    /* Messages */
    .seeker-msg {
        background: linear-gradient(135deg, rgba(70,130,180,0.15), rgba(100,149,237,0.08));
        border-left: 3px solid #6495ed;
        border-radius: 0 20px 20px 0;
        padding: 1.25rem 1.75rem;
        margin: 1.25rem 0;
        font-family: 'Crimson Pro', serif;
        color: #e8e8f0;
    }
    
    .advisor-msg {
        background: linear-gradient(135deg, rgba(255,215,0,0.08), rgba(218,165,32,0.04));
        border-left: 3px solid #ffd700;
        border-radius: 0 20px 20px 0;
        padding: 1.75rem;
        margin: 1.25rem 0;
        font-family: 'Crimson Pro', serif;
        color: #f0f0f5;
        line-height: 2;
    }
    
    .msg-label {
        font-family: 'Cormorant Garamond', serif;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .seeker-label { color: #6495ed; }
    .advisor-label { color: #ffd700; }
    
    /* Crisis alert */
    .crisis-alert {
        background: linear-gradient(135deg, rgba(220,53,69,0.2), rgba(220,53,69,0.1));
        border: 2px solid #dc3545;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12122a 0%, #0a0a18 100%);
    }
    
    .sidebar-header {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.3rem;
        color: #ffd700;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255,215,0,0.2);
    }
    
    .sidebar-section {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1rem;
        color: #ffd700;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #ffd700, #daa520);
        color: #1a1a2e;
        font-family: 'Cormorant Garamond', serif;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #fff8dc, #ffd700);
        box-shadow: 0 8px 25px rgba(255,215,0,0.35);
        transform: translateY(-2px);
    }
    
    /* Radio buttons for mode selection */
    .stRadio > div {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stRadio > div > label {
        color: #e8e8f0 !important;
        font-family: 'Crimson Pro', serif !important;
    }
    
    /* Dividers */
    .sacred-divider {
        text-align: center;
        color: rgba(255,215,0,0.4);
        margin: 2rem 0;
        font-size: 1.5rem;
        letter-spacing: 1.5rem;
    }
    
    /* Listen button */
    .listen-btn {
        background: rgba(255,215,0,0.1);
        border: 1px solid rgba(255,215,0,0.3);
        border-radius: 20px;
        padding: 0.4rem 1rem;
        color: #ffd700;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .listen-btn:hover {
        background: rgba(255,215,0,0.2);
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Text areas */
    .stTextArea textarea {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,215,0,0.2);
        border-radius: 15px;
        color: #e8e8f0;
        font-family: 'Crimson Pro', serif;
        font-size: 1.05rem;
    }
    
    .stTextArea textarea:focus {
        border-color: rgba(255,215,0,0.5);
        box-shadow: 0 0 15px rgba(255,215,0,0.1);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05);
        border-color: rgba(255,215,0,0.2);
    }
    """
    
    # Prayer mode - more minimal, darker, centered
    if mode == "prayer":
        base_css += """
        .stApp {
            background: radial-gradient(ellipse at center, #1a1a2e 0%, #0a0a12 100%);
        }
        
        .prayer-container {
            max-width: 600px;
            margin: 0 auto;
            padding-top: 15vh;
            text-align: center;
        }
        
        .candle-icon {
            font-size: 4rem;
            animation: flicker 3s infinite;
        }
        
        @keyframes flicker {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
            25%, 75% { opacity: 0.9; }
        }
        """
    
    return f"<style>{base_css}</style>"


# =====================================================================
# TEXT-TO-SPEECH FUNCTION
# =====================================================================
def text_to_speech(text: str) -> str:
    """Convert text to speech and return path to audio file."""
    if not TTS_AVAILABLE:
        return None
    
    try:
        if TTS_METHOD == "macos_say":
            # Clean text for speech (remove markdown symbols)
            clean_text = text.replace('*', '').replace('_', '').replace('#', '').replace('`', '')
            clean_text = clean_text.replace('\n', ' ').replace('  ', ' ')
            
            # Create temp files
            aiff_path = tempfile.mktemp(suffix='.aiff')
            wav_path = tempfile.mktemp(suffix='.wav')
            
            # Use Samantha voice (calm female) at slower rate
            result = subprocess.run([
                'say',
                '-v', 'Samantha',
                '-r', '150',
                '-o', aiff_path,
                clean_text
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                st.error(f"Say command failed: {result.stderr}")
                return None
            
            # Convert AIFF to WAV for browser compatibility
            convert_result = subprocess.run([
                'afconvert',
                '-f', 'WAVE',
                '-d', 'LEI16',
                aiff_path,
                wav_path
            ], capture_output=True, text=True)
            
            # Clean up AIFF
            try:
                os.unlink(aiff_path)
            except:
                pass
            
            if convert_result.returncode == 0 and os.path.exists(wav_path):
                return wav_path
            else:
                # Fallback: return AIFF if conversion failed
                return aiff_path if os.path.exists(aiff_path) else None
            
        elif TTS_METHOD == "pyttsx3":
            import pyttsx3
            temp_path = tempfile.mktemp(suffix='.wav')
            engine = pyttsx3.init()
            engine.setProperty('rate', 140)
            
            voices = engine.getProperty('voices')
            for voice in voices:
                if any(name in voice.name.lower() for name in ['samantha', 'karen', 'daniel']):
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            return temp_path
            
    except Exception as e:
        st.error(f"Voice generation failed: {e}")
        return None
    
    return None


# =====================================================================
# SESSION STATE INITIALIZATION
# =====================================================================
def init_session():
    """Initialize all session state variables."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.user_id = get_user_id(st.session_state.session_id)
        st.session_state.memory = load_user_memory(st.session_state.user_id)
        st.session_state.memory["visit_count"] = st.session_state.memory.get("visit_count", 0) + 1
        
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "ui_mode" not in st.session_state:
        st.session_state.ui_mode = "standard"
    if "selected_traditions" not in st.session_state:
        st.session_state.selected_traditions = ["All Traditions"]
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = False
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0
    if "daily_wisdom" not in st.session_state:
        st.session_state.daily_wisdom = None
    if "show_compare" not in st.session_state:
        st.session_state.show_compare = False


init_session()

# Apply custom CSS
st.markdown(get_custom_css(st.session_state.ui_mode), unsafe_allow_html=True)


# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-header">🕊️ Divine Wisdom Guide</div>', unsafe_allow_html=True)
    
    # Mode Selection - Using radio for cleaner layout
    st.markdown('<div class="sidebar-section">✨ Experience Mode</div>', unsafe_allow_html=True)
    
    mode_options = {
        "standard": "🌟 Standard — Full guidance",
        "prayer": "🕯️ Prayer — Contemplative",
        "journal": "📖 Journal — Reflective",
        "meditation": "🧘 Meditation — Guided"
    }
    
    selected_mode = st.radio(
        "Choose mode:",
        options=list(mode_options.keys()),
        format_func=lambda x: mode_options[x],
        index=list(mode_options.keys()).index(st.session_state.ui_mode),
        label_visibility="collapsed"
    )
    
    if selected_mode != st.session_state.ui_mode:
        st.session_state.ui_mode = selected_mode
        st.rerun()
    
    st.markdown("---")
    
    # Voice Output Status
    st.markdown('<div class="sidebar-section">🔊 Voice Output</div>', unsafe_allow_html=True)
    
    if TTS_AVAILABLE:
        st.success(f"✓ Voice enabled ({TTS_METHOD})")
        st.caption("Click '🔊 Listen' buttons to hear responses")
    else:
        st.warning("Voice not available")
        st.caption("On macOS, the 'say' command should work automatically")
    
    st.markdown("---")
    
    # Tradition Selection
    st.markdown('<div class="sidebar-section">📜 Wisdom Sources</div>', unsafe_allow_html=True)
    
    traditions_list = ["All Traditions"] + list(TRADITIONS.keys())
    selected = st.multiselect(
        "Draw wisdom from:",
        options=traditions_list,
        default=st.session_state.selected_traditions,
        label_visibility="collapsed"
    )
    st.session_state.selected_traditions = selected if selected else ["All Traditions"]
    
    # Show tradition details
    with st.expander("ℹ️ About Traditions"):
        for tradition, info in TRADITIONS.items():
            st.markdown(f"**{info['icon']} {tradition}**")
            st.caption(info['description'])
    
    st.markdown("---")
    
    # Settings
    st.markdown('<div class="sidebar-section">⚙️ Settings</div>', unsafe_allow_html=True)
    
    st.session_state.show_sources = st.checkbox(
        "Show scripture sources",
        value=st.session_state.show_sources
    )
    
    # Compare traditions button
    if st.button("⚖️ Compare Traditions", use_container_width=True):
        st.session_state.show_compare = True
        st.rerun()
    
    if st.button("🔄 New Session", use_container_width=True):
        save_user_memory(st.session_state.user_id, st.session_state.memory)
        st.session_state.chat_history = []
        st.session_state.message_count = 0
        st.session_state.daily_wisdom = None
        st.rerun()
    
    # Memory indicator
    st.markdown("---")
    visit_count = st.session_state.memory.get("visit_count", 1)
    themes = st.session_state.memory.get("themes", [])
    st.caption(f"🧠 Visit #{visit_count}")
    if themes:
        st.caption(f"Themes: {', '.join(themes[-3:])}")


# =====================================================================
# HELPER: Display response with optional TTS
# =====================================================================
def display_response_with_voice(response_text: str, key: str, is_crisis: bool = False):
    """Display a response with optional voice playback button AFTER the message."""
    
    if is_crisis:
        st.markdown(f'<div class="crisis-alert">{response_text}</div>', unsafe_allow_html=True)
        return
    
    # Display the message first
    st.markdown(f"""
    <div class="advisor-msg">
        <div class="msg-label advisor-label">✨ Divine Wisdom</div>
        {response_text}
    </div>
    """, unsafe_allow_html=True)
    
    # Voice playback button AFTER the message
    if TTS_AVAILABLE:
        # Use a container to keep button and audio together
        col1, col2 = st.columns([1, 4])
        with col1:
            listen_clicked = st.button("🔊 Listen", key=f"tts_{key}", help="Hear this wisdom spoken aloud")
        
        if listen_clicked:
            with st.spinner("🎙️ Generating voice..."):
                audio_path = text_to_speech(response_text)
                if audio_path and os.path.exists(audio_path):
                    with open(audio_path, 'rb') as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/wav")
                    try:
                        os.unlink(audio_path)
                    except:
                        pass
                else:
                    st.error("Could not generate voice. Please try again.")


# =====================================================================
# MAIN CONTENT - PRAYER MODE
# =====================================================================
if st.session_state.ui_mode == "prayer":
    st.markdown("""
    <div class="prayer-container">
        <div class="candle-icon">🕯️</div>
        <h2 style="font-family: 'Cormorant Garamond', serif; color: #ffd700; margin: 2rem 0;">
            A Space for Contemplation
        </h2>
        <p style="font-family: 'Crimson Pro', serif; color: #9090a8; font-style: italic;">
            Speak what is in your heart...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    prayer_input = st.text_area(
        "Your prayer or reflection:",
        placeholder="Share what weighs upon your heart...",
        height=120,
        label_visibility="collapsed",
        key="prayer_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🙏 Offer to the Light", use_container_width=True):
            if prayer_input.strip():
                with st.spinner(""):
                    traditions_filter = None if "All Traditions" in st.session_state.selected_traditions else st.session_state.selected_traditions
                    
                    response, docs, is_crisis = ask_question(
                        prayer_input,
                        traditions=traditions_filter,
                        user_memory=st.session_state.memory,
                        mode="prayer",
                        message_count=st.session_state.message_count
                    )
                    
                    st.session_state.chat_history.append((prayer_input, response, docs, is_crisis))
                    st.session_state.message_count += 1
                    st.session_state.memory = add_exchange(
                        st.session_state.memory, 
                        prayer_input, 
                        response,
                        traditions_filter
                    )
                    save_user_memory(st.session_state.user_id, st.session_state.memory)
                    st.rerun()
    
    # Show last response
    if st.session_state.chat_history:
        last_q, last_a, _, is_crisis = st.session_state.chat_history[-1]
        st.markdown("---")
        display_response_with_voice(last_a, "prayer_response", is_crisis)


# =====================================================================
# MAIN CONTENT - JOURNAL MODE
# =====================================================================
elif st.session_state.ui_mode == "journal":
    st.markdown('<h1 class="main-title">📖 Spiritual Journal</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">A space for reflection and gentle insight</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="wisdom-card">
        <em>Write freely about your day, your thoughts, your struggles, or your joys. 
        I will listen and reflect back what I notice, offering wisdom when it may help.</em>
    </div>
    """, unsafe_allow_html=True)
    
    journal_entry = st.text_area(
        "Today's Reflection:",
        placeholder="What's on your mind today? Write freely...",
        height=200,
        key="journal_entry"
    )
    
    if st.button("📝 Reflect", use_container_width=True):
        if journal_entry.strip():
            with st.spinner("Contemplating your words..."):
                reflection = generate_journal_reflection(
                    journal_entry,
                    st.session_state.memory
                )
                
                st.session_state.memory = add_journal_entry(
                    st.session_state.memory,
                    journal_entry,
                    reflection
                )
                save_user_memory(st.session_state.user_id, st.session_state.memory)
                
                st.markdown("### 🌿 Reflection")
                display_response_with_voice(reflection, "journal_reflection")
    
    # Past journal entries
    if st.session_state.memory.get("journal_entries"):
        with st.expander("📚 Past Reflections"):
            for entry in reversed(st.session_state.memory["journal_entries"][-5:]):
                st.markdown(f"**{entry['date'][:10]}**")
                st.markdown(f"> {entry['entry'][:200]}...")
                st.markdown("---")


# =====================================================================
# MAIN CONTENT - MEDITATION MODE
# =====================================================================
elif st.session_state.ui_mode == "meditation":
    st.markdown('<h1 class="main-title">🧘 Guided Meditation</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Personalized meditations drawn from sacred wisdom</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="wisdom-card">
        <em>Tell me what you need today—peace, clarity, courage, healing—and I will 
        create a guided meditation just for you, woven with wisdom from the traditions you've chosen.</em>
    </div>
    """, unsafe_allow_html=True)
    
    meditation_need = st.text_input(
        "What do you need from this meditation?",
        placeholder="e.g., 'I need peace after a stressful day' or 'Help me find courage'",
        key="meditation_need"
    )
    
    if st.button("🧘 Generate Meditation", use_container_width=True):
        if meditation_need.strip():
            with st.spinner("Creating your meditation..."):
                traditions_filter = None if "All Traditions" in st.session_state.selected_traditions else st.session_state.selected_traditions
                
                response, docs, _ = ask_question(
                    meditation_need,
                    traditions=traditions_filter,
                    user_memory=st.session_state.memory,
                    mode="meditation",
                    message_count=st.session_state.message_count
                )
                
                st.markdown("### 🌸 Your Guided Meditation")
                display_response_with_voice(response, "meditation_response")
                
                if st.session_state.show_sources and docs:
                    with st.expander("📖 Wisdom Sources"):
                        for doc in docs:
                            tradition = doc.metadata.get('tradition', 'Unknown')
                            scripture = doc.metadata.get('scripture_name', 'Unknown')
                            st.markdown(f"**{tradition} - {scripture}**")
                            st.caption(doc.page_content[:300] + "...")


# =====================================================================
# MAIN CONTENT - COMPARATIVE THEOLOGY
# =====================================================================
elif st.session_state.show_compare:
    st.markdown('<h1 class="main-title">⚖️ Comparative Wisdom</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Explore how different traditions approach life\'s great questions</p>', unsafe_allow_html=True)
    
    compare_topic = st.text_input(
        "What topic would you like to explore across traditions?",
        placeholder="e.g., 'forgiveness', 'suffering', 'love', 'death', 'purpose'",
        key="compare_topic"
    )
    
    compare_traditions_list = st.multiselect(
        "Select traditions to compare (2-5 recommended):",
        options=list(TRADITIONS.keys()),
        default=["Christianity", "Buddhism", "Hinduism"],
        key="compare_traditions"
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔍 Compare", use_container_width=True):
            if compare_topic.strip() and len(compare_traditions_list) >= 2:
                with st.spinner("Exploring wisdom across traditions..."):
                    comparison, docs = compare_traditions(compare_topic, compare_traditions_list)
                    
                    st.markdown("### 🌍 Comparative Insights")
                    display_response_with_voice(comparison, "comparison_response")
    
    with col2:
        if st.button("← Back to Advisor", use_container_width=True):
            st.session_state.show_compare = False
            st.rerun()


# =====================================================================
# MAIN CONTENT - STANDARD MODE
# =====================================================================
else:
    # Header
    st.markdown('<h1 class="main-title">🕊️ Divine Wisdom Guide</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-title">Seek guidance from the sacred wisdom of humanity\'s spiritual traditions</p>',
        unsafe_allow_html=True
    )
    
    # Daily Wisdom
    if not st.session_state.daily_wisdom:
        themes = st.session_state.memory.get("themes", [])
        traditions = None if "All Traditions" in st.session_state.selected_traditions else st.session_state.selected_traditions
        wisdom, tradition, scripture = generate_daily_wisdom(themes, traditions)
        st.session_state.daily_wisdom = (wisdom, tradition, scripture)
    
    wisdom_text, tradition, scripture = st.session_state.daily_wisdom
    
    st.markdown(f"""
    <div class="daily-wisdom">
        <div style="font-size: 2rem; margin-bottom: 1rem;">✨</div>
        <div class="daily-wisdom-text">{wisdom_text}</div>
        <div class="daily-wisdom-source">— {tradition}{f' • {scripture}' if scripture else ''}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Listen button AFTER daily wisdom - small and centered
    if TTS_AVAILABLE:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🔊 Listen", key="tts_daily", help="Hear daily wisdom"):
                with st.spinner("🎙️"):
                    audio_path = text_to_speech(wisdom_text)
                    if audio_path and os.path.exists(audio_path):
                        with open(audio_path, 'rb') as f:
                            audio_bytes = f.read()
                        st.audio(audio_bytes, format="audio/wav")
                        try:
                            os.unlink(audio_path)
                        except:
                            pass
    
    # Returning user greeting
    if len(st.session_state.chat_history) == 0:
        greeting = get_returning_user_greeting(st.session_state.memory)
        if greeting:
            st.markdown(f'<div class="wisdom-card"><em>{greeting}</em></div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="wisdom-card">
                <em>{ADVISOR_GREETING}</em>
                <br><br>
                You may ask about:
                <ul>
                    <li>Life decisions and moral dilemmas</li>
                    <li>Relationships and forgiveness</li>
                    <li>Finding purpose and meaning</li>
                    <li>Dealing with suffering and grief</li>
                    <li>Cultivating peace and wisdom</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Display conversation history
    if st.session_state.chat_history:
        for idx, (q, a, sources, is_crisis) in enumerate(st.session_state.chat_history):
            st.markdown(f"""
            <div class="seeker-msg">
                <div class="msg-label seeker-label">🙏 You</div>
                {q}
            </div>
            """, unsafe_allow_html=True)
            
            display_response_with_voice(a, f"response_{idx}", is_crisis)
            
            if st.session_state.show_sources and sources and not is_crisis:
                with st.expander(f"📖 Sources ({len(sources)} passages)"):
                    for doc in sources:
                        tradition = doc.metadata.get('tradition', 'Unknown')
                        scripture = doc.metadata.get('scripture_name', 'Unknown')
                        st.markdown(f"**{tradition} - {scripture}**")
                        st.caption(doc.page_content[:400] + "...")
        
        st.markdown('<div class="sacred-divider">✦ ✦ ✦</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown("### 💭 What guidance do you seek?")
    
    user_question = st.text_area(
        "Share your question:",
        placeholder="Share what's on your mind, ask for guidance, or seek wisdom...",
        height=100,
        label_visibility="collapsed",
        key="main_question"
    )
    
    col1, col2 = st.columns([3, 1])
    with col2:
        ask_btn = st.button("🙏 Seek Wisdom", use_container_width=True)
    
    if ask_btn:
        if user_question.strip():
            with st.spinner("🕊️ Contemplating..."):
                traditions_filter = None if "All Traditions" in st.session_state.selected_traditions else st.session_state.selected_traditions
                
                history = [(q, a) for q, a, _, _ in st.session_state.chat_history]
                
                response, docs, is_crisis = ask_question(
                    user_question,
                    traditions=traditions_filter,
                    conversation_history=history,
                    user_memory=st.session_state.memory,
                    mode="standard",
                    message_count=st.session_state.message_count
                )
                
                st.session_state.chat_history.append((user_question, response, docs, is_crisis))
                st.session_state.message_count += 1
                
                if not is_crisis:
                    st.session_state.memory = add_exchange(
                        st.session_state.memory,
                        user_question,
                        response,
                        traditions_filter
                    )
                    save_user_memory(st.session_state.user_id, st.session_state.memory)
                
                st.rerun()
        else:
            st.warning("Please share your question or concern.")


# =====================================================================
# FOOTER
# =====================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-family: 'Crimson Pro', serif; font-size: 0.9rem; padding: 1rem;">
    <em>"The beginning of wisdom is the definition of terms."</em> — Socrates
    <br><br>
    <span style="font-size: 0.8rem;">
    This advisor draws upon sacred texts for guidance. For health, legal, or emergency matters, please consult professionals.
    <br>If you're in crisis: <strong>988</strong> (Suicide & Crisis Lifeline)
    </span>
</div>
""", unsafe_allow_html=True)

# Save memory
save_user_memory(st.session_state.user_id, st.session_state.memory)
