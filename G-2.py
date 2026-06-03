import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import streamlit.components.v1 as components

# --- 1. SET PAGE CONFIG ---
st.set_page_config(
    page_title="G-2 Quantum Agro-Lab", 
    page_icon="🧬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED CSS INJECTION ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(74, 222, 128, 0.2);
    }
    .hero-container {
        background: linear-gradient(90deg, rgba(34, 197, 94, 0.1) 0%, rgba(30, 41, 59, 0.5) 100%);
        border-left: 5px solid #22c55e;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin-bottom: 30px;
    }
    .hero-title {
        font-size: 45px !important;
        font-weight: 800 !important;
        color: #4ade80 !important;
        text-shadow: 0 0 15px rgba(74,222,128,0.4);
        margin: 0;
    }
    .hero-subtitle {
        color: #94a3b8 !important;
        font-size: 16px;
        margin-top: 5px;
    }
    .user-box {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white !important;
        padding: 15px;
        border-radius: 18px 18px 2px 18px;
        margin: 10px 0px 10px auto;
        max-width: 75%;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .ai-box {
        background: rgba(30, 41, 59, 0.9);
        color: #f1f5f9 !important;
        padding: 18px;
        border-radius: 18px 18px 18px 2px;
        margin: 10px auto 10px 0px;
        max-width: 85%;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        border: 1px solid rgba(74, 222, 128, 0.2);
        line-height: 1.6;
    }
    .stSlider > label, .stMetric label { color: #4ade80 !important; font-weight: 600; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #4ade80 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. JAVASCRIPT ---
components.html("""
<script>
    console.log("%c🌱 G-2 MULTI-MODE ENGINE ACTIVATED", "color: #4ade80; font-size: 20px; font-weight: bold;");
    parent.document.title = "🧬 G-2: Multi-Mode AI";
</script>
""", height=0, width=0)

# --- 4. SIDEBAR PANEL (WITH MODE SELECTION) ---
with st.sidebar:
    st.markdown("<h2 style='color:#4ade80; text-align:center;'>🔬 G-2 CORE PANEL</h2>", unsafe_allow_html=True)
    
    # SVG Logo Code Embedded Directly
    st.markdown("""
    <div style='text-align:center;'>
        <svg width="80" height="80" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path d="M50,90 C50,90 20,60 20,30 C20,10 50,10 50,10 C50,10 80,10 80,30 C80,60 50,90 50,90 Z" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round"/>
            <circle cx="50" cy="40" r="5" fill="#4ade80" />
            <path d="M50,45 L50,85" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/>
            <path d="M50,60 L32,42" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/>
            <circle cx="32" cy="42" r="3" fill="#4ade80" />
            <path d="M50,70 L68,52" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/>
            <circle cx="68" cy="52" r="3" fill="#4ade80" />
        </svg>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Select System Configuration</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # --- YAHAN MODE SELECTBOX DALA HAI ---
    ai_mode = st.selectbox(
        "⚙️ CHOOSE AI MODE:",
        ["Normal Mode", "Basic Farming Mode", "Agro-Lab Mode"]
    )
    
    st.markdown("---")
    st.subheader("📊 Mode Status")
    st.metric(label="Active Neural Grid", value=ai_mode.split()[0], delta="Ready")
    
    st.markdown("---")
    st.subheader("🎛️ Simulation Tweaks")
    temp_target = st.slider("Incubator Temp (°C)", 10, 60, 28)
    ph_target = st.slider("Substrate pH", 3.0, 10.0, 6.2)

# --- 5. MAIN HERO INTERFACE ---
st.markdown(f"""
<div class="hero-container">
    <h1 class="hero-title">🌱 G-2: Multi-Mode AI</h1>
    <div class="hero-subtitle">Currently Operating in <b>{ai_mode}</b> — Powered by Gemini-Flash Core</div>
</div>
""", unsafe_allow_html=True)

# --- 6. API KEY & MODEL INITIALIZATION ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key missing! Check your Streamlit Secrets.")
    st.stop()

# Auto-finder block ko simple rakh ke direct flash chala rahe hai jo bina errors ke direct chalega
model = genai.GenerativeModel("gemini-1.5-flash")

# --- 7. CONVERSATION STATE & MEMORY REBOOT ON MODE CHANGE ---
# Agar user mode badle, toh chat history purani refresh ho jaye taaki AI confuse na ho
if "current_mode" not in st.session_state:
    st.session_state.current_mode = ai_mode

if st.session_state.current_mode != ai_mode:
    st.session_state.current_mode = ai_mode
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = []
    st.rerun()

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# Past Chat History Render
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-box"><b>You:</b><br>{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-box"><b>🧬 G-2 [{ai_mode.split()[0]}]:</b><br>{message["content"]}</div>', unsafe_allow_html=True)

# --- 8. VOICE GENERATOR ENGINE ---
def generate_voice(text):
    clean_text = text.split("---")[0]  
    tts = gTTS(text=clean_text[:250], lang='hi') 
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    return audio_bytes

# --- 9. MODE BEHAVIOR CONFIGURATOR (PROMPT INJECTION) ---
# Mode ke hisaab se system instructions banti hain
if ai_mode == "Normal Mode":
    system_instruction = "You are a helpful, friendly general assistant. Answer the question normally and casually."
elif ai_mode == "Basic Farming Mode":
    system_instruction = "You are a simple village agricultural advisor. Explain concepts in very simple, easy-to-understand Hinglish/Hindi. Focus on local farming practices, crops, seasons, and simple solutions for Indian farmers. Avoid heavy scientific words."
elif ai_mode == "Agro-Lab Mode":
    system_instruction = f"You are an expert Agro-Chemical scientist in a high-tech quantum laboratory. Provide highly technical, deep scientific answers, including chemical formulas, molecular docking data, gene names, and strict lab procedures. Current simulated context: Temp={temp_target}°C, pH={ph_target}."

# --- 10. INPUT & PROCESSING ---
user_query = st.chat_input(f"Type your query for {ai_mode}...")

if user_query:
    st.markdown(f'<div class="user-box"><b>You:</b><br>{user_query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.spinner(f"🔬 G-2 [{ai_mode.split()[0]}] Engine processing..."):
        try:
            # System instruction ko user query ke sath merge karke bhejna
            master_prompt = f"{system_instruction}\n\nUser Question: {user_query}"
            response = st.session_state.chat_session.send_message(master_prompt)
            
            st.markdown(f'<div class="ai-box"><b>🧬 G-2 Engine:</b><br>{response.text}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            audio_file = generate_voice(response.text)
            st.audio(audio_file, format="audio/mp3")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"⚠️ Grid Error: {e}")
            
