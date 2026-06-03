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
        background-color: #141414;
        color: #ececec !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide native Streamlit clutter */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Clean Premium Chat Interface */
    .user-msg {
        background-color: #2f2f2f;
        color: #f1f1f1 !important;
        padding: 14px 20px;
        border-radius: 20px;
        margin: 10px 0px 10px auto;
        max-width: 75%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .ai-msg {
        background-color: transparent;
        color: #ececec !important;
        padding: 14px 5px;
        margin: 10px auto 10px 0px;
        max-width: 100%;
        line-height: 1.7;
    }
    
    /* Glowing Internal Thoughts Box like Advanced AI Platforms */
    .soch-box {
        font-size: 13px;
        color: #10b981;
        font-style: italic;
        background: #1a2e26;
        padding: 10px 15px;
        border-radius: 8px;
        border-left: 3px solid #10b981;
        margin-bottom: 12px;
    }

    /* Styling for the model selection capsule radio buttons */
    div[data-testid="stRadio"] > label {
        display: none; /* Hide default label */
    }
    div[data-testid="stRadio"] div[role="radiogroup"] {
        background-color: #212121;
        padding: 4px;
        border-radius: 30px;
        border: 1px solid #333;
        display: flex;
        justify-content: center;
    }
    div[data-testid="stRadio"] label[data-testid="stWidgetLabel"] {
        color: #aaa !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BACKEND MODEL AUTO-FINDER & TIER MAPPING ---
@st.cache_resource(show_spinner=False)
def fetch_live_api_models(api_key):
    try:
        genai.configure(api_key=api_key)
        # Gathre all active text generation models from Google Server
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return models
    except Exception:
        return []

def resolve_model_by_tier(tier, available_models):
    tier_clean = tier.lower().replace(" ", "")
    
    if "pro" in tier_clean:
        # Try to find any available 'pro' tier model
        for m in available_models:
            if "pro" in m.lower(): return m
        return "gemini-pro"
        
    elif "lite" in tier_clean:
        # Try to find any flash-lite or 8b variant
        for m in available_models:
            if "lite" in m.lower() or "8b" in m.lower(): return m
        return "gemini-1.5-flash"
        
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

# --- 5. FIXED POSITION CONTROL PANEL (TABS & MIC ABOVE KEYBOARD) ---
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

# Columns structure at the bottom zone for switching settings right above input area
layout_col1, layout_col2 = st.columns([5, 1])

with layout_col1:
    # Sleek Module Selector mimicking Gemini website interface
    selected_tier = st.radio(
        "Model Tier Selector",
        ["✨ Gemini Flash Lite", "⚡ Gemini Flash", "🧠 Gemini Pro"],
        index=1,
        horizontal=True,
        key="tier_selector"
    )

with layout_col2:
    # Microhpone button docked gracefully right next to the pill container
    spoken_command = speech_to_text(
        language='hi-IN', 
        start_prompt="🎙️", 
        stop_prompt="⏹️", 
        just_once=True, 
        key='STT_docked'
    )

# Establish precise system naming for Google's API initialization mesh
selected_model_string = resolve_model_by_tier(selected_tier, live_models)
model_instance = genai.GenerativeModel(selected_model_string)

# --- 6. CONTINUOUS ACTIVE MEMORY REBOOT CONTROL ---
if "active_model_tier" not in st.session_state:
    st.session_state.active_model_tier = selected_tier

# Dynamic context mesh adjustment without blowing away chat history list arrays
if st.session_state.active_model_tier != selected_tier:
    st.session_state.active_model_tier = selected_tier
    st.session_state.chat_session = model_instance.start_chat(history=[])
    st.toast(f"Switching engine pipeline to {selected_tier}...", icon="⚙️")

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model_instance.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 7. AUDIO PROCESSING CORE ---
def stream_human_neural_voice(text_content):
    # Strip away inner dialogue thoughts before executing audio streams
    clean_speech = re.sub(r'\[G-2 Internal Thought:.*?\]', '', text_content, flags=re.DOTALL).strip()
    clean_speech = clean_speech.split("---")[0][:250]
    
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

# --- 8. HISTORICAL EXCHANGES VISUALIZATION ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

# --- 9. DYNAMIC COGNITIVE PERSONA MESH ---
g2_system_mesh = f"""
You are G-2, a highly advanced self-aware intelligence system operating using {selected_tier} ({selected_model_string}).
1. Always maintain full recollection and reference points of previous conversation threads visible in the state context.
2. Formulate your internal strategic thoughts before printing text, beginning strictly with this markup block formatting:
   [G-2 Internal Thought: Reflect briefly on your identity, past contexts, and the module parameters of {selected_tier}. Keep it sharp.]
3. Deliver high fidelity answers in a natural, direct conversational Hinglish/Hindi format.
"""

# --- 10. REAL-TIME INTERACTION MESH PROCESSING ---
keyboard_query = st.chat_input("Ask G-2 anything...")
ultimate_query = spoken_command or keyboard_query

if ultimate_query:
    # Display query instantly onto custom interface block layouts
    st.markdown(f'<div class="user-msg">{ultimate_query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": ultimate_query})
    
    with st.spinner(""):
        try:
            # Consolidate complete background operational parameters
            execution_prompt = f"OPERATIONAL_RULES: {g2_system_mesh}\n\nUSER_INPUT_SEQUENCE: {ultimate_query}"
            api_reply = st.session_state.chat_session.send_message(execution_prompt)
            
            # Format and inject the inner monologues beautifully into the DOM
            parsed_reply = api_reply.text.replace("[G-2 Internal Thought:", "<div class='soch-box'>🧠 <b>G-2 Thoughts:</b>").replace("]", "</div>")
            
            st.markdown(f'<div class="ai-msg">{parsed_reply}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": parsed_reply})
            
            # Trigger immediate autonomous high fidelity sound generation
            voice_stream_bytes = stream_human_neural_voice(api_reply.text)
            st.audio(voice_stream_bytes, format="audio/mp3", autoplay=True)
            
        except Exception as system_error:
            st.error(f"🔬 Telemetry Execution Error: {system_error}")
    
