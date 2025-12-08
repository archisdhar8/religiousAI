"""
Voice Integration Module for Divine Wisdom Guide

Provides speech-to-text (STT) and text-to-speech (TTS) capabilities
for a more immersive, confessional-style experience.

OPTIONAL: Requires additional dependencies:
    pip install openai-whisper sounddevice soundfile numpy
    
For TTS, choose one:
    pip install TTS           # Coqui TTS (high quality, needs GPU)
    pip install pyttsx3       # Offline, simpler, works on all platforms
    pip install elevenlabs    # Cloud-based, very realistic (paid)
"""

import os
import tempfile
from typing import Optional, Callable
from config import STT_MODEL, TTS_VOICE, VOICE_ENABLED

# Track what's available
_whisper_available = False
_tts_available = False
_tts_engine = None

# Try to import Whisper for STT
try:
    import whisper
    _whisper_available = True
except ImportError:
    pass

# Try to import TTS options
try:
    import pyttsx3
    _tts_engine = "pyttsx3"
    _tts_available = True
except ImportError:
    pass

if not _tts_available:
    try:
        from TTS.api import TTS as CoquiTTS
        _tts_engine = "coqui"
        _tts_available = True
    except ImportError:
        pass


def is_voice_available() -> dict:
    """Check what voice features are available."""
    return {
        "enabled": VOICE_ENABLED,
        "stt_available": _whisper_available,
        "tts_available": _tts_available,
        "tts_engine": _tts_engine
    }


# =====================================================================
# SPEECH-TO-TEXT (Whisper)
# =====================================================================

_whisper_model = None

def load_whisper_model():
    """Load Whisper model (lazy loading)."""
    global _whisper_model
    if _whisper_model is None and _whisper_available:
        _whisper_model = whisper.load_model(STT_MODEL)
    return _whisper_model


def transcribe_audio(audio_path: str) -> Optional[str]:
    """
    Transcribe audio file to text using Whisper.
    
    Args:
        audio_path: Path to audio file (wav, mp3, etc.)
    
    Returns:
        Transcribed text or None if failed
    """
    if not _whisper_available:
        return None
    
    try:
        model = load_whisper_model()
        result = model.transcribe(audio_path)
        return result["text"].strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return None


def transcribe_audio_bytes(audio_bytes: bytes, format: str = "wav") -> Optional[str]:
    """
    Transcribe audio from bytes.
    
    Args:
        audio_bytes: Raw audio bytes
        format: Audio format (wav, mp3, etc.)
    
    Returns:
        Transcribed text or None if failed
    """
    if not _whisper_available:
        return None
    
    try:
        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        # Transcribe
        result = transcribe_audio(temp_path)
        
        # Clean up
        os.unlink(temp_path)
        
        return result
    except Exception as e:
        print(f"Transcription error: {e}")
        return None


# =====================================================================
# TEXT-TO-SPEECH
# =====================================================================

_pyttsx_engine = None
_coqui_tts = None


def init_tts():
    """Initialize TTS engine."""
    global _pyttsx_engine, _coqui_tts
    
    if _tts_engine == "pyttsx3" and _pyttsx_engine is None:
        _pyttsx_engine = pyttsx3.init()
        # Configure for calm, slow speech
        _pyttsx_engine.setProperty('rate', 130)  # Slower than default
        voices = _pyttsx_engine.getProperty('voices')
        # Try to find a calm-sounding voice
        for voice in voices:
            if 'daniel' in voice.name.lower() or 'david' in voice.name.lower():
                _pyttsx_engine.setProperty('voice', voice.id)
                break
    
    elif _tts_engine == "coqui" and _coqui_tts is None:
        # Use a good quality model
        _coqui_tts = CoquiTTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")


def speak_text(text: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Convert text to speech.
    
    Args:
        text: Text to speak
        output_path: Optional path to save audio file
    
    Returns:
        Path to audio file, or None if played directly/failed
    """
    if not _tts_available:
        return None
    
    try:
        init_tts()
        
        if _tts_engine == "pyttsx3":
            if output_path:
                _pyttsx_engine.save_to_file(text, output_path)
                _pyttsx_engine.runAndWait()
                return output_path
            else:
                _pyttsx_engine.say(text)
                _pyttsx_engine.runAndWait()
                return None
        
        elif _tts_engine == "coqui":
            if output_path is None:
                output_path = tempfile.mktemp(suffix=".wav")
            _coqui_tts.tts_to_file(text=text, file_path=output_path)
            return output_path
        
    except Exception as e:
        print(f"TTS error: {e}")
        return None


def speak_text_async(text: str, callback: Optional[Callable] = None):
    """
    Convert text to speech asynchronously.
    
    Args:
        text: Text to speak
        callback: Optional callback when done
    """
    import threading
    
    def _speak():
        speak_text(text)
        if callback:
            callback()
    
    thread = threading.Thread(target=_speak)
    thread.start()


# =====================================================================
# STREAMLIT AUDIO RECORDER (for use in app.py)
# =====================================================================

def get_audio_recorder_html() -> str:
    """
    Returns HTML/JS for an audio recorder widget.
    Can be embedded in Streamlit via st.components.v1.html
    """
    return """
    <div style="text-align: center; padding: 20px;">
        <button id="recordBtn" style="
            background: linear-gradient(135deg, #ffd700, #daa520);
            border: none;
            border-radius: 50%;
            width: 80px;
            height: 80px;
            cursor: pointer;
            font-size: 2rem;
            transition: all 0.3s ease;
        ">🎤</button>
        <p id="status" style="color: #9090a8; margin-top: 10px;">Click to speak</p>
        <audio id="audioPlayback" controls style="display: none; margin-top: 10px;"></audio>
    </div>
    
    <script>
        let mediaRecorder;
        let audioChunks = [];
        const recordBtn = document.getElementById('recordBtn');
        const status = document.getElementById('status');
        const audioPlayback = document.getElementById('audioPlayback');
        
        recordBtn.onclick = async () => {
            if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = (e) => {
                    audioChunks.push(e.data);
                };
                
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    audioPlayback.src = audioUrl;
                    audioPlayback.style.display = 'block';
                    
                    // Send to Streamlit (would need proper integration)
                    // For now, just play back
                };
                
                mediaRecorder.start();
                recordBtn.textContent = '⏹️';
                recordBtn.style.background = 'linear-gradient(135deg, #dc3545, #c82333)';
                status.textContent = 'Recording... Click to stop';
            } else {
                mediaRecorder.stop();
                recordBtn.textContent = '🎤';
                recordBtn.style.background = 'linear-gradient(135deg, #ffd700, #daa520)';
                status.textContent = 'Click to speak again';
            }
        };
    </script>
    """


# =====================================================================
# CONVENIENCE FUNCTIONS
# =====================================================================

def process_voice_input(audio_bytes: bytes) -> Optional[str]:
    """
    Full pipeline: audio bytes -> transcribed text.
    """
    if not VOICE_ENABLED or not _whisper_available:
        return None
    
    return transcribe_audio_bytes(audio_bytes)


def generate_voice_response(text: str) -> Optional[str]:
    """
    Full pipeline: text -> audio file path.
    """
    if not VOICE_ENABLED or not _tts_available:
        return None
    
    return speak_text(text)

