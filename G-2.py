import streamlit as st
import google.generativeai as genai
import edge_tts
import asyncio
import io
import re
import streamlit.components.v1 as components
from streamlit_mic_recorder import speech_to_text

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Gemini G-2 Intelligence", 
    page_icon="✨", 
    layout="centered", # Centered layout is exactly like ChatGPT/Gemini
    initial_sidebar_state="collapsed"
)

# --- 2. ULTRA-CLEAN CHATGPT/GEMINI THEME CSS ---
st.markdown("""
<style>
    /* Global App Background & Minimal look */
    .stApp {
        background-color: #141414; /* Deep dark grey/black like ChatGPT */
        color: #ececec !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Hide native Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;} /* Hide sidebar completely */
    
    /* Clean Premium Chat Interface */
    .user-msg {
        background-color: #2f2f2f;
        color: #f1f1f1 !important;
        padding: 14px 20px;
        border-radius: 20px;
        margin: 10px 0px 10px auto;
        max-width: 75%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        font-size: 15px;
    }
    .ai-msg {
        background-color: transparent;
        color: #ececec !important;
        padding: 14px 5px;
        margin: 10px auto 10px 0px;
        max-width: 100%;
        line-height: 1.7;
        font-size: 15px;
    }
    
    /* Glowing Internal Thoughts Box like Advanced AI Platforms */
    .soch-box {
        font-size: 13px;
        color: #a855f7; /* Purple vibe for AI thoughts */
        font-style: italic;
        background: rgba(168, 85, 247, 0.1);
        padding: 10px 15px;
        border-radius: 8px;
        border-left: 3px solid #a855f7;
        margin-bottom: 12px;
    }

    /* Styling the Control Bar (Model Switcher) */
    div.stRadio > div[role="radiogroup"] {
        flex-direction: row;
        background-color: #212121;
        padding: 5px;
        border-radius: 25px;
        border: 1px solid #333;
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    div.stRadio > label { display: none; } /* Hide label text above radio */
    
    .st-emotion-cache-1wivap2 { padding-bottom: 0px !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. BACKEND MODEL AUTO-FINDER & TIER MAPPING ---
@st.cache_resource(show_spinner=False)
def fetch_live_api_models(api_key):
    try:
        genai.configure(api_key=api_key)
        # Gather all active text generation models from Google Server
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return models
    except Exception:
        return []

def resolve_model_by_tier(tier, available_models):
    # Smart matching based on what the user selects vs what Google API allows
    tier_lower = tier.lower()
    
    if "pro" in tier_lower:
        for m in available_models:
            if "pro" in m.lower(): return m
        return "gemini-pro"
        
    elif "lite" in tier_lower:
        # Looking for latest lite/8b models
        for m in available_models:
            if "lite" in m.lower() or "8b" in m.lower(): return m
        return "gemini-1.5-flash" # Fallback
        
    else:
        # Standard Flash mode
        for m in available_models:
            if "flash" in m.lower() and "lite" not in m.lower(): return m
        return "gemini-1.5-flash"

# --- 4. SECURE API CONFIGURATION ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    live_models = fetch_live_api_models(api_key)
except Exception:
    st.error("⚠️ CRITICAL FAULT: GEMINI_API_KEY Missing in Secrets Configuration.")
    st.stop()

# --- 5. INITIALIZE STATE & MEMORY ---
if "active_model_tier" not in st.session_state:
    st.session_state.active_model_tier = "⚡ Gemini Flash" # Default

if "chat_session" not in st.session_state:
    # Dummy initialization, will be overwritten by active model
    dummy_model = genai.GenerativeModel("gemini-1.5-flash")
    st.session_state.chat_session = dummy_model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. RENDER CHAT HISTORY (Top Area) ---
# Dikhne mein ekdum clean scrollable chat
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

# Spacing to push controls down near the input box
st.markdown("<br><br>", unsafe_allow_html=True)

# --- 7. FIXED POSITION CONTROL PANEL (TABS & MIC JUST ABOVE KEYBOARD) ---
# Ye area tere input box ke theek upar aayega
control_col1, control_col2 = st.columns([5, 1], vertical_alignment="center")

with control_col1:
    selected_tier = st.radio(
        "Module",
        ["✨ Gemini Flash Lite", "⚡ Gemini Flash", "🧠 Gemini Pro"],
        index=["✨ Gemini Flash Lite", "⚡ Gemini Flash", "🧠 Gemini Pro"].index(st.session_state.active_model_tier),
        horizontal=True,
        key="tier_selector"
    )

with control_col2:
    # Mic feature
    spoken_command = speech_to_text(
        language='hi-IN', 
        start_prompt="🎙️", 
        stop_prompt="⏹️", 
        just_once=True, 
        key='STT_docked'
    )

# Establish precise system naming for Google's API initialization
selected_model_string = resolve_model_by_tier(selected_tier, live_models)
model_instance = genai.GenerativeModel(selected_model_string)

# Dynamic context mesh adjustment WITHOUT losing history
if st.session_state.active_model_tier != selected_tier:
    st.session_state.active_model_tier = selected_tier
    # Migrate history to new model
    st.session_state.chat_session = model_instance.start_chat(
        history=st.session_state.chat_session.history
    )
    st.rerun() # Refresh to show UI update smoothly

# --- 8. AUDIO PROCESSING CORE ---
def stream_human_neural_voice(text_content):
    # Strip away inner dialogue thoughts before speaking
    clean_speech = re.sub(r'\[G-2 Internal Thought:.*?\]', '', text_content, flags=re.DOTALL).strip()
    clean_speech = clean_speech.split("---")[0][:250] # Kept short for fast audio
    
    async def run_edge_tts():
        communicator = edge_tts.Communicate(clean_speech, "hi-IN-MadhurNeural")
        raw_buffer = b""
        async for segment in communicator.stream():
            if segment["type"] == "audio": raw_buffer += segment["data"]
        return raw_buffer
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    audio_output_bytes = loop.run_until_complete(run_edge_tts())
    loop.close()
    return audio_output_bytes

# --- 9. DYNAMIC COGNITIVE PERSONA MESH ---
g2_system_mesh = f"""
You are G-2, a highly advanced self-aware intelligence system operating via the {selected_tier} module ({selected_model_string}).
1. Always maintain full recollection of previous conversation threads.
2. IMPORTANT SOCH FORMAT: Before answering, formulate your internal strategic thoughts starting EXACTLY with this tag:
   [G-2 Internal Thought: Briefly analyze the request and module parameters.]
3. Deliver your final answer in a natural, direct conversational Hinglish/Hindi format. Keep it concise.
"""

# --- 10. REAL-TIME INPUT & PROCESSING ---
# Native Streamlit chat input stuck at the bottom
keyboard_query = st.chat_input("Message G-2...")

# Combine both mic and keyboard inputs
ultimate_query = spoken_command or keyboard_query

if ultimate_query:
    st.markdown(f'<div class="user-msg">{ultimate_query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": ultimate_query})
    
    with st.spinner("✨ Generating..."):
        try:
            execution_prompt = f"SYSTEM_RULES: {g2_system_mesh}\n\nUSER_MESSAGE: {ultimate_query}"
            api_reply = st.session_state.chat_session.send_message(execution_prompt)
            
            # Parse the inner monologue beautifully
            parsed_reply = api_reply.text.replace("[G-2 Internal Thought:", "<div class='soch-box'>🧠 <b>G-2 Thoughts:</b>").replace("]", "</div>")
            
            st.markdown(f'<div class="ai-msg">{parsed_reply}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": parsed_reply})
            
            # Autonomous voice playback
            voice_stream_bytes = stream_human_neural_voice(api_reply.text)
            st.audio(voice_stream_bytes, format="audio/mp3", autoplay=True)
            
        except Exception as system_error:
            st.error(f"⚠️ API Error: {system_error}")
            
