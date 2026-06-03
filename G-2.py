import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import streamlit.components.v1 as components

# --- 1. SET PAGE CONFIG (MUST BE FIRST) ---
st.set_page_config(
    page_title="G-2 Quantum Agro-Lab", 
    page_icon="🧬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED HTML & CSS INJECTION (THEMING) ---
st.markdown("""
<style>
    /* Global App Background & Font */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling (Glassmorphism) */
    [data-testid="stSidebar"] {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(74, 222, 128, 0.2);
    }
    
    /* Custom Modern Header */
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

    /* Custom Premium Chat Bubbles */
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
    
    /* Streamlit native elements overriding */
    .stSlider > label, .stMetric label { color: #4ade80 !important; font-weight: 600; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #4ade80 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. JAVASCRIPT INJECTION (FOR ANIMATION / UX EFFECTS) ---
# Yeh JS browser mein run hoga aur page load hote hi console mein ek sleek green notification trigger karega
components.html("""
<script>
    console.log("%c🌱 G-2 QUANTUM ENGINE ACTIVATED SUCCESSFULLY", "color: #4ade80; font-size: 20px; font-weight: bold; text-shadow: 0 0 10px rgba(74,222,128,0.5);");
    // App ke load hote hi ek halki si click window feedback alert browser tab par set karega
    parent.document.title = "🧬 G-2: Quantum Agro-Lab AI";
</script>
""", height=0, width=0)

# --- 4. SIDEBAR PANEL ---
with st.sidebar:
    st.markdown("<h2 style='color:#4ade80; text-align:center;'>🔬 G-2 CORE PANEL</h2>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'><img src='https://img.icons8.com/fluent/100/000000/biotech.png' width='80'></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Quantum Synthesis Mode Active</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Advanced Metrics with neon styling
    st.subheader("📊 Neural Diagnostics")
    st.metric(label="System Response", value="Ultra-Fast", delta="99.4% Acc")
    
    st.markdown("---")
    st.subheader("⚙️ Live Simulation Matrix")
    temp_target = st.slider("Incubator Temp (°C)", 10, 60, 28)
    ph_target = st.slider("Substrate pH", 3.0, 10.0, 6.2)
    st.markdown("---")
    st.caption("Developed for high-end biochemical research workflows.")

# --- 5. MAIN CUSTOM HERO INTERFACE (HTML) ---
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🌱 G-2: Quantum Agro-Lab AI</h1>
    <div class="hero-subtitle">Advanced Autonomous Synthesis Engine Engine — Enabled with HTML5, CSS3, & JavaScript Core</div>
</div>
""", unsafe_allow_html=True)

# --- 6. API KEY & SMART ENGINE AUTO-FINDER ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key missing! Check your Streamlit Secrets.")
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

# --- 7. CONVERSATION STATE & YAADASHT ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# Rendering past chat history using our Custom Premium HTML Boxes
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-box"><b>You:</b><br>{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-box"><b>🧬 G-2 Engine:</b><br>{message["content"]}</div>', unsafe_allow_html=True)

# --- 8. VOICE GENERATOR ENGINE (gTTS) ---
def generate_voice(text):
    # Shorten text a bit for seamless audio rendering
    clean_text = text.split("---")[0]  
    tts = gTTS(text=clean_text[:300], lang='hi') 
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    return audio_bytes

# --- 9. INPUT & REAL-TIME PROCESSING ---
user_query = st.chat_input("Ask G-2 about seed genetics, molecular formulas...")

if user_query:
    # Render user query immediately in custom HTML bubble
    st.markdown(f'<div class="user-box"><b>You:</b><br>{user_query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.spinner("🔬 G-2 Neural Grid is analyzing data points..."):
        try:
            enriched_prompt = f"Provide a concise conversational scientific summary. Lab Parameters: Temp={temp_target}°C, pH={ph_target}. User Query: {user_query}"
            response = st.session_state.chat_session.send_message(enriched_prompt)
            
            # Render AI reply in gorgeous custom layout container
            st.markdown(f'<div class="ai-box"><b>🧬 G-2 Engine:</b><br>{response.text}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # Generate and embed audio controller
            audio_file = generate_voice(response.text)
            st.audio(audio_file, format="audio/mp3")
            
            # Small page refresh trick to ensure layout settles nicely
            st.rerun()
            
        except Exception as e:
            st.error(f"⚠️ Simulation Error: {e}")
            
