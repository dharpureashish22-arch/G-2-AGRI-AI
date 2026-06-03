import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="G-2 Agro-Lab", page_icon="🌱", layout="centered")
st.title("🌱 G-2: Advanced Learning AI")

# --- 1. API Key Setup ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key missing in Streamlit Secrets!")
    st.stop()

# --- 2. Knowledge Base (Continuous Learning System) ---
@st.cache_data # Isse AI baar-baar file load karke time waste nahi karega
def load_knowledge():
    knowledge_text = ""
    # Check karega ki Knowledge_Base naam ka folder hai ya nahi
    if os.path.exists("Knowledge_Base"):
        for filename in os.listdir("Knowledge_Base"):
            if filename.endswith(".txt"):
                file_path = os.path.join("Knowledge_Base", filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    knowledge_text += f"\n--- Document: {filename} ---\n"
                    knowledge_text += file.read() + "\n"
    return knowledge_text

# AI saari txt files ka gyan apne dimaag mein load kar lega
lab_data = load_knowledge()

# --- 3. Conversation Memory (Yaadasht) ---
model = genai.GenerativeModel("gemini-1.5-pro")

# Agar chat history nahi hai, toh nayi memory banayega
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# Pichli saari baatein (Chat history) screen par dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. Chat Interface ---
st.caption("G-2 is ready. Apni query type karein (Pichli baatein yaad rahengi).")
user_query = st.chat_input("G-2 se apna sawal poochein...")

if user_query:
    # User ka message screen par dikhana
    st.chat_message("user").markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # AI ko Knowledge base + User ka naya sawal dono bhejna
    full_prompt = f"""
    You are G-2, an advanced Agro-Chemist AI.
    
    Here is your continuously updated Knowledge Base. Use this data strictly if it relates to the user's query:
    {lab_data}
    
    User's Question: {user_query}
    """
    
    # AI se jawab lena
    with st.chat_message("assistant"):
        with st.spinner("G-2 is analyzing..."):
            try:
                # send_message function automatically memory maintain karta hai
                response = st.session_state.chat_session.send_message(full_prompt)
                st.markdown(response.text)
                
                # Jawab ko memory mein save karna
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error connecting to brain: {e}")
