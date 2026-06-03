import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# --- 1. PREMIUM PAGE CONFIGURATION ---
st.set_page_config(page_title="G-2 Agro-Lab", page_icon="🔬", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main-title { font-size: 42px !important; font-weight: 700 !important; color: #1E88E5; }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("## 🔬 G-2 System Panel")
    st.caption("Version: 5.0 (Voice-Enabled 🔊)")
    st.markdown("---")
    temp_target = st.slider("Target Temp (°C)", 15, 50, 25)
    ph_target = st.slider("Soil pH Target", 4.0, 9.0, 6.5)

# --- 3. MAIN INTERFACE ---
st.markdown("<h1 class='main-title'>🌱 G-2: Voice-Enabled AI</h1>", unsafe_allow_html=True)
st.write("Ab G-2 aapke sawalon ka jawab bol kar bhi dega! Type karein aur suniye.")
st.markdown("---")

# --- 4. API & SMART MODEL SETUP ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key missing!")
    st.stop()

valid_model_name = "gemini-1.5-flash"
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower():
            valid_model_name = m.name
            break
except Exception:
    pass

model = genai.GenerativeModel(valid_model_name)

# --- 5. MEMORY SETUP ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. VOICE GENERATOR FUNCTION ---
def generate_voice(text):
    # 'hi' set kiya hai taaki woh Hindi aur English dono sentences ko natural accent mein padh sake
    tts = gTTS(text=text, lang='hi') 
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    return audio_bytes

# --- 7. CHAT & VOICE OUTPUT ---
user_query = st.chat_input("G-2 se apna sawal poochein...")

if user_query:
    st.chat_message("user").markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        with st.spinner(f"G-2 is thinking and generating voice using {valid_model_name.replace('models/', '')}... 🔊"):
            try:
                # Prompt modify kiya hai taaki audio bahut lamba aur boring na ho
                enriched_prompt = f"Keep the answer short, concise, and conversational (no long complex tables). Context: Temp={temp_target}°C, pH={ph_target}. Query: {user_query}"
                response = st.session_state.chat_session.send_message(enriched_prompt)
                
                # 1. Pehle text screen par print karega
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                # 2. Phir uski awaaz banakar audio player dikhayega
                audio_file = generate_voice(response.text)
                st.audio(audio_file, format="audio/mp3")
                
            except Exception as e:
                st.error(f"⚠️ API Error: {e}")
                
