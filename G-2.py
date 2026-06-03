import streamlit as st
import google.generativeai as genai

# --- 1. Page Setup ---
st.set_page_config(page_title="G-2 Autonomous Lab", page_icon="🌍", layout="centered")
st.title("🌍 G-2: Autonomous Research AI")
st.caption("G-2 AI is ready! Aapke agricultural aur scientific sawalon ke jawab ke liye.")

# --- 2. API Key Setup ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key missing! Streamlit settings mein 'Secrets' check karein.")
    st.stop()

# --- 3. Model Setup (100% Error-Free Line) ---
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools="google_search_retrieval"
)

# --- 4. Chat Memory Setup (Yaadasht) ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purani chat history screen par dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. User Chat Interface ---
user_query = st.chat_input("G-2 se apna sawal poochein (Jaise: 'Latest Nano-Urea research batao')...")

if user_query:
    # User ka sawal screen par dikhana
    st.chat_message("user").markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # AI se jawab lena
    with st.chat_message("assistant"):
        with st.spinner("G-2 soch raha hai... 💡"):
            try:
                response = st.session_state.chat_session.send_message(user_query)
                st.markdown(response.text)
                
                # Jawab ko memory mein save karna
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error aagaya bhai: {e}")
                
