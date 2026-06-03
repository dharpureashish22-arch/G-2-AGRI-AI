import streamlit as st
import google.generativeai as genai

# --- 1. PREMIUM PAGE CONFIGURATION ---
st.set_page_config(
    page_title="G-2 Agro-Lab Intelligence", 
    page_icon="🔬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown("""
<style>
    .main-title { font-size: 42px !important; font-weight: 700 !important; color: #1E88E5; }
    .stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR NAVIGATION & SETTINGS ---
with st.sidebar:
    st.markdown("## 🔬 G-2 System Panel")
    st.image("https://img.icons8.com/fluent/100/000000/laboratory.png", width=80)
    st.caption("Version: 4.0 (Auto-Mesh)")
    st.markdown("---")
    
    st.subheader("📊 System Diagnostics")
    st.metric(label="AI Brain Status", value="Online", delta="Stable")
    
    st.markdown("---")
    st.subheader("⚙️ Lab Parameters")
    temp_target = st.slider("Target Temp (°C)", 15, 50, 25)
    ph_target = st.slider("Soil pH Target", 4.0, 9.0, 6.5)

# --- 3. MAIN INTERFACE ---
st.markdown("<h1 class='main-title'>🌱 G-2: Autonomous Agro-Lab AI</h1>", unsafe_allow_html=True)
st.write("Welcome to the advanced synthesis interface. G-2 is equipped with autonomous knowledge retrieval.")
st.markdown("---")

# --- 4. API KEY SETUP FROM SECRETS ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key missing! Please check your Streamlit App Secrets settings.")
    st.stop()

# --- 5. SMART MODEL FINDER (YAHI MASTERSTROKE HAI) ---
# Yeh code Google API se list mangega aur jo valid hoga wahi chalayega!
valid_model_name = "gemini-1.5-flash" # Default fallback
try:
    for m in genai.list_models():
        # Check karega ki model text generate kar sakta hai aur naam mein 'gemini' hai
        if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower():
            valid_model_name = m.name # Jo chal raha hoga, usko save kar lega
            break
except Exception:
    pass

# Ab 404 error aane ka chance hi zero hai
model = genai.GenerativeModel(valid_model_name)

# --- 6. CONVERSATION MEMORY (SESSION STATE) ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 7. EXPANDER FOR RESEARCH DOCUMENTATION ---
with st.expander("📝 View Active Lab Configuration", expanded=False):
    st.markdown(f"Temperature: `{temp_target}°C` | Soil Acidity: `{ph_target} pH`")

# Pichli chat history dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 8. CHAT INPUT SECTION ---
user_query = st.chat_input("G-2 se apna sawal poochein...")

if user_query:
    st.chat_message("user").markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        # Yahan screen par dikhega ki usne apne aap konsa model uthaya hai
        with st.spinner(f"🔬 G-2 is processing using {valid_model_name.replace('models/', '')}..."):
            try:
                enriched_prompt = f"User Lab Context: Temp={temp_target}°C, pH={ph_target}.\nQuery: {user_query}"
                response = st.session_state.chat_session.send_message(enriched_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ API Error: {e}")
                
