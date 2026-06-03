import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import time
import streamlit.components.v1 as components

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(
    page_title="G-2 Enterprise Agro-Lab", 
    page_icon="🧬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED CSS & ANIMATIONS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #09090b 0%, #18181b 100%);
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: rgba(24, 24, 27, 0.8) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(34, 197, 94, 0.3);
    }
    .pro-header {
        background: linear-gradient(90deg, rgba(21, 128, 61, 0.1) 0%, rgba(24, 24, 27, 0.8) 100%);
        border-left: 6px solid #22c55e;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 30px;
    }
    .user-msg {
        background: linear-gradient(135deg, #0369a1 0%, #0c4a6e 100%);
        color: white !important;
        padding: 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 12px 0px 12px auto;
        max-width: 80%;
        box-shadow: 0 4px 15px rgba(3, 105, 161, 0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .ai-msg {
        background: rgba(39, 39, 42, 0.9);
        color: #f8fafc !important;
        padding: 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 12px auto 12px 0px;
        max-width: 85%;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        border: 1px solid rgba(34, 197, 94, 0.3);
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)

components.html("""
<script>
    console.log("%c🧬 G-2 ENTERPRISE SYSTEM ONLINE", "color: #22c55e; font-size: 18px; font-weight: bold;");
</script>
""", height=0, width=0)

# --- 3. SYSTEM FUNCTIONS (CACHED FOR SPEED) ---
@st.cache_resource(show_spinner=False)
def initialize_ai(api_key):
    genai.configure(api_key=api_key)
    valid_name = "gemini-1.5-flash"
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower():
                valid_name = m.name
                break
    except Exception:
        pass
    return genai.GenerativeModel(valid_name), valid_name

def generate_voice(text):
    clean_text = text.split("---")[0][:250]
    tts = gTTS(text=clean_text, lang='hi') 
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    return audio_bytes

def export_chat_log(messages):
    log = "G-2 ENTERPRISE CHAT LOG\n" + "="*30 + "\n\n"
    for m in messages:
        role = "USER" if m["role"] == "user" else "G-2 AI"
        log += f"[{role}]: {m['content']}\n\n"
    return log

# --- 4. ENTERPRISE SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#22c55e; text-align:center;'>🧬 G-2 COMMAND</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    ai_mode = st.selectbox("⚙️ SELECT PROTOCOL:", ["Normal Assistant", "Agro-Lab Pro", "Village Farming"])
    
    st.markdown("---")
    st.subheader("🎛️ Live Environment")
    temp_target = st.slider("Incubator Temp (°C)", 10, 60, 28)
    ph_target = st.slider("Substrate pH", 3.0, 10.0, 6.2)
    
    # Fake Live Telemetry Chart (Professional UI touch)
    st.caption("Live Sensor Telemetry")
    chart_data = [temp_target + (i * 0.5) for i in range(10)]
    st.line_chart(chart_data, height=150, color="#22c55e")

    st.markdown("---")
    # Export Chat Feature
    if st.session_state.get("messages"):
        chat_data = export_chat_log(st.session_state.messages)
        st.download_button(label="📥 Download Lab Report", data=chat_data, file_name="G2_Report.txt", mime="text/plain")

# --- 5. MAIN UI HEADER ---
st.markdown(f"""
<div class="pro-header">
    <h1 style='color: #22c55e; margin:0;'>🌱 G-2 Enterprise Terminal</h1>
    <p style='color: #a1a1aa; margin-top:5px;'>Protocol Status: <b>{ai_mode}</b> | Encrypted Connection</p>
</div>
""", unsafe_allow_html=True)

# --- 6. SECURE API CONNECTION ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    model, model_name = initialize_ai(api_key)
except Exception:
    st.error("⚠️ CRITICAL FAULT: API Key Missing in System Secrets.")
    st.stop()

# --- 7. DYNAMIC SESSION STATE ---
if "current_mode" not in st.session_state:
    st.session_state.current_mode = ai_mode
    st.toast("System Initialized Successfully!", icon="🟢")

if st.session_state.current_mode != ai_mode:
    st.session_state.current_mode = ai_mode
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = []
    st.toast(f"Protocol Switched to {ai_mode}", icon="🔄")
    st.rerun()

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 8. RENDER CHAT HISTORY ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-msg"><b>User:</b><br>{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-msg"><b>🧬 G-2 [{ai_mode.split()[0]}]:</b><br>{message["content"]}</div>', unsafe_allow_html=True)

# --- 9. AI INSTRUCTIONS (MODE LOGIC) ---
if ai_mode == "Normal Assistant":
    sys_instruction = "You are a highly capable enterprise AI assistant. Be concise and professional."
elif ai_mode == "Agro-Lab Pro":
    sys_instruction = f"You are a top-tier agricultural scientist. Use deep scientific terms, molecular data, and professional formatting. Context: Temp={temp_target}°C, pH={ph_target}."
else:
    sys_instruction = "You are a local farming expert. Speak in simple Hindi/Hinglish. Give practical, low-cost Indian farming advice."

# --- 10. INPUT PROCESSING & OUTPUT ---
user_query = st.chat_input("Enter command or query sequence...")

if user_query:
    st.markdown(f'<div class="user-msg"><b>User:</b><br>{user_query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.spinner("🧬 Processing quantum parameters..."):
        try:
            prompt = f"System Command: {sys_instruction}\nUser Query: {user_query}"
            response = st.session_state.chat_session.send_message(prompt)
            
            st.markdown(f'<div class="ai-msg"><b>🧬 G-2:</b><br>{response.text}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # Generate Audio
            audio_file = generate_voice(response.text)
            st.audio(audio_file, format="audio/mp3")
            
            st.toast("Analysis Complete", icon="✅")
            time.sleep(0.5)
            st.rerun()
            
        except Exception as e:
            st.error(f"⚠️ System Failure: {e}")
            
            
