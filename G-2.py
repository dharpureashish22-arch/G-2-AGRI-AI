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
    st.caption("Version: 3.5 (Autonomous-Mesh)")
    st.markdown("---")
    
    st.subheader("📊 System Diagnostics")
    st.metric(label="AI Brain Status", value="Online", delta="Stable")
    st.metric(label="Search Pipeline", value="Connected", delta="Live")
    
    st.markdown("---")
    st.subheader("⚙️ Lab Parameters")
    temp_target = st.slider("Target Temp (°C)", 15, 50, 25)
    ph_target = st.slider("Soil pH Target", 4.0, 9.0, 6.5)
    
    st.markdown("---")
    st.info("💡 Pro Tip: Custom molecules design karne ke liye exact inputs ka use karein.")

# --- 3. MAIN INTERFACE ---
st.markdown("<h1 class='main-title'>🌱 G-2: Autonomous Agro-Lab AI</h1>", unsafe_allow_html=True)
st.write("Welcome to the advanced synthesis interface. G-2 is equipped with autonomous knowledge retrieval to engineer bio-solutions in real-time.")

# Quick Stats Row
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Category 1:** Seed Genetics 🧬")
with col2:
    st.success("**Category 2:** Nano-Fertilizers 🧪")
with col3:
    st.warning("**Category 3:** Bio-Pesticides 🌾")

st.markdown("---")

# --- 4. API KEY SETUP FROM SECRETS ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key missing! Please check your Streamlit App Secrets settings.")
    st.stop()

# --- 5. MODEL INITIALIZATION ---
model = genai.GenerativeModel("gemini-1.5-flash")

# --- 6. CONVERSATION MEMORY (SESSION STATE) ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 7. EXPANDER FOR RESEARCH DOCUMENTATION ---
with st.expander("📝 View Active Lab Configuration & Guidelines", expanded=False):
    st.markdown(f"""
    * **Current Lab Context:** System optimized for high-yield precision agronomy.
    * **Environment Constraints:** Temperature: `{temp_target}°C` | Soil Acidity: `{ph_target} pH`.
    * **Core Engines Activated:** Genome Sequencer, Molecular Docking Simulator, Cheminformatics Pipeline.
    """)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 8. CHAT INPUT SECTION ---
user_query = st.chat_input("G-2 se apna sawal poochein ya chemical structure request karein...")

if user_query:
    # Display user question
    st.chat_message("user").markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Process AI Response
    with st.chat_message("assistant"):
        with st.spinner("🔬 G-2 Molecular Engine is processing context & search web..."):
            try:
                enriched_prompt = f"""
                User Lab Condition context: Temperature={temp_target}°C, Soil pH={ph_target}.
                User Query: {user_query}
                Please provide a deeply technical, comprehensive and well-formatted scientific analysis.
                """
                
                response = st.session_state.chat_session.send_message(enriched_prompt)
                st.markdown(response.text)
                
                # Save answer to state
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ Execution Error: {e}")
