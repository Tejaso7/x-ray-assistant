import os
import base64
import tempfile
from PIL import Image
import streamlit as st
from fpdf import FPDF
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo

# --- SESSION STATE ---
if "GOOGLE_API_KEY" not in st.session_state:
    st.session_state.GOOGLE_API_KEY = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.title("🔐 API Configuration")
    if not st.session_state.GOOGLE_API_KEY:
        api_key = st.text_input("Enter Google API Key:", type="password")
        st.caption("[Get your API key](https://aistudio.google.com/apikey)")
        if api_key:
            st.session_state.GOOGLE_API_KEY = api_key
            st.success("✅ API Key saved!")
            st.rerun()
    else:
        st.success("API Key configured")
        if st.button("🔄 Reset Key"):
            st.session_state.GOOGLE_API_KEY = None
            st.rerun()

# --- AI AGENT INIT ---
medical_agent = Agent(
    model=Gemini(
        api_key=st.session_state.GOOGLE_API_KEY,
        id="gemini-2.0-flash-exp"
    ),
    tools=[DuckDuckGo()],
    markdown=True
) if st.session_state.GOOGLE_API_KEY else None

# --- PROMPT TEMPLATE ---
def generate_prompt(image_type="X-ray", region="Chest"):
    return f"""
You are a skilled radiologist. Analyze the uploaded {image_type} of the {region} and structure your response with:

You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging. Analyze the patient's medical image and structure your response as follows:

### 1. Image Type & Region
- Specify imaging modality (X-ray/MRI/CT/Ultrasound/etc.)
- Identify the patient's anatomical region and positioning
- Comment on image quality and technical adequacy

### 2. Key Findings
- List primary observations systematically
- Note any abnormalities in the patient's imaging with precise descriptions
- Include measurements and densities where relevant
- Describe location, size, shape, and characteristics
- Rate severity: Normal/Mild/Moderate/Severe

### 3. Diagnostic Assessment
- Provide primary diagnosis with confidence level
- List differential diagnoses in order of likelihood
- Support each diagnosis with observed evidence from the patient's imaging
- Note any critical or urgent findings

### 4. Patient-Friendly Explanation
- Explain the findings in simple, clear language that the patient can understand
- Avoid medical jargon or provide clear definitions
- Include visual analogies if helpful
- Address common patient concerns related to these findings

### 5. Research Context
IMPORTANT: Use the DuckDuckGo search tool to:
- Find recent medical literature about similar cases
- Search for standard treatment protocols
- Provide a list of relevant medical links of them too
- Research any relevant technological advances
- Include 2-3 key references to support your analysis

Format your response using clear markdown headers and bullet points. Be concise yet thorough.
"""

# --- UI ---
st.set_page_config(page_title="🧠 Medical Imaging Diagnosis", layout="wide")
st.title("🧠 Medical Imaging Diagnosis Agent")
st.markdown("> Upload a medical image and get a detailed AI-based diagnostic report.")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📤 Upload Image", "📋 Diagnosis", "💬 Chat with AI"])

with tab1:
    uploaded_files = st.file_uploader("Upload medical images (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Uploaded Image: {uploaded_file.name}", use_column_width=True)

            with st.expander("🧾 Image Details"):
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**Format:** {image.format}")
                st.write(f"**Dimensions:** {image.size[0]} x {image.size[1]} px")

            if st.button(f"🔍 Analyze {uploaded_file.name}", key=uploaded_file.name):
                image_path = f"temp_{uploaded_file.name}"
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                with st.spinner("🔄 Analyzing image..."):
                    try:
                        prompt = generate_prompt()
                        response = medical_agent.run(prompt, images=[image_path])
                        st.session_state.analysis_result = response.content
                        st.success("✅ Analysis complete!")
                        os.remove(image_path)
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("Please upload medical images to proceed.")

with tab2:
    if st.session_state.analysis_result:
        st.markdown(st.session_state.analysis_result)
        st.caption("⚠️ This is an AI-generated report. Always consult a certified medical professional.")

        # --- PDF Export ---
        if st.button("📄 Export Report as PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in st.session_state.analysis_result.split('\n'):
                pdf.multi_cell(0, 10, line)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                pdf.output(tmpfile.name)
                with open(tmpfile.name, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<a href="data:application/pdf;base64,{base64_pdf}" download="diagnosis_report.pdf">📥 Download Report</a>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                os.remove(tmpfile.name)
    else:
        st.info("No analysis available. Please analyze an image first.")

with tab3:
    st.subheader("💬 Chat with the Medical AI")
    user_input = st.text_input("Ask a question about the diagnosis or your symptoms:")
    if st.button("💡 Get Answer"):
        if user_input and medical_agent:
            full_prompt = f"""You are a medical assistant. The user has received the following analysis:\n\n{st.session_state.analysis_result}\n\nNow answer this question:\n{user_input}"""
            with st.spinner("Thinking..."):
                try:
                    followup = medical_agent.run(full_prompt)
                    st.session_state.chat_history.append((user_input, followup.content))
                except Exception as e:
                    st.error(f"Failed to get response: {e}")
        else:
            st.warning("Please enter a question.")

    if st.session_state.chat_history:
        for i, (q, a) in enumerate(reversed(st.session_state.chat_history), 1):
            st.markdown(f"**Q{i}:** {q}")
            st.markdown(f"**A{i}:** {a}")
