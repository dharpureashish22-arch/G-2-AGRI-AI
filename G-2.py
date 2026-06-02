import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Agro-Lab AI", page_icon="🔬")

st.title("🔬 Personal Agro-Lab AI")
st.write("Upload a scientific document, and I will analyze it to create precise formulas.")

# Step 1: Enter API Key
api_key = st.text_input("Enter your free Gemini API Key:", type="password")

# Step 2: Upload Lab Data
uploaded_file = st.file_uploader("Upload Lab Data / Research Paper (.txt)", type=["txt"])

# Step 3: Ask the Question
user_query = st.text_area("What formula or analysis do you need from this data?")

if st.button("Run Lab Analysis"):
    if not api_key:
        st.error("Please enter your API key.")
    elif not uploaded_file:
        st.error("Please upload a .txt file so the AI has factual data to read.")
    elif not user_query:
        st.warning("Please enter a question.")
    else:
        # Read the uploaded file
        document_text = uploaded_file.read().decode("utf-8")
        
        try:
            # Connect to the free API
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-pro")
            
            # Strict instructions so it behaves like a scientist
            strict_prompt = f"""
            You are a professional Agro-Chemist. 
            Read the following scientific document carefully:
            {document_text}
            
            Based ONLY on the document above, answer this request: {user_query}
            If the answer is not in the document, reply: "Insufficient lab data to synthesize this formula."
            """
            
            with st.spinner("Analyzing molecular data..."):
                response = model.generate_content(strict_prompt)
                
            st.success("Analysis Complete!")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Error connecting to lab servers: {e}")
