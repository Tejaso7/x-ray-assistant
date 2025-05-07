import os
from PIL import Image
import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile

# Session State
if "GOOGLE_API_KEY" not in st.session_state:
    st.session_state.GOOGLE_API_KEY = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    if not st.session_state.GOOGLE_API_KEY:
        api_key = st.text_input("🔑 Enter your Google API Key:", type="password")
        st.caption("Get it from [Google AI Studio](https://aistudio.google.com/apikey)")
        if api_key:
            st.session_state.GOOGLE_API_KEY = api_key
            st.success("API Key saved! ✅")
            st.rerun()
    else:
        st.success("✅ API Key is configured")
        if st.button("🔄 Reset API Key"):
            st.session_state.GOOGLE_API_KEY = None
            st.rerun()
    st.markdown("---")
    st.info("Upload a medical image to receive AI-powered diagnostic analysis.")

# AI Medical Agent Initialization
medical_agent = Agent(
    model=Gemini(api_key=st.session_state.GOOGLE_API_KEY, id="gemini-2.0-pro"),
    tools=[DuckDuckGo()],
    markdown=True
) if st.session_state.GOOGLE_API_KEY else None

# Diagnostic Prompt
analysis_prompt = """
You are a highly skilled medical imaging expert. Analyze the uploaded image using the following structure:

### 1. Image Type & Region
- Imaging modality (e.g. X-ray, MRI, CT)
- Anatomical region & positioning
- Image quality and technical notes

### 2. Key Findings
- Observations (normal/abnormal)
- Size, shape, location, characteristics
- Severity rating: Normal/Mild/Moderate/Severe

### 3. Diagnostic Assessment
- Primary & differential diagnoses
- Confidence levels
- Urgency, critical notes

### 4. Patient-Friendly Summary
- Plain-language explanation
- Visual analogy if applicable
- Reassurance, next steps

### 5. Research Context
- Search for recent medical literature
- Summarize standard protocols
- Add 2-3 reference links
"""

# App UI Layout
st.title("🧠 Medical Imaging Diagnosis Assistant")
st.subheader("Upload a medical image and receive expert-level AI analysis.")

upload_container = st.container()
display_container = st.container()
analysis_container = st.container()
chat_container = st.container()

with upload_container:
    uploaded_file = st.file_uploader(
        "📤 Upload Image", type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, JPEG, PNG"
    )

if uploaded_file:
    image = Image.open(uploaded_file)
    width, height = image.size
    aspect_ratio = width / height
    new_width = 512
    new_height = int(new_width / aspect_ratio)
    resized_image = image.resize((new_width, new_height))

    with display_container:
        st.image(resized_image, caption="📍 Uploaded Image", use_column_width=True)
        analyze_btn = st.button("🔬 Analyze Image")

    if analyze_btn and medical_agent:
        with st.spinner("Analyzing the image..."):
            temp_img_path = os.path.join(tempfile.gettempdir(), "input_image.png")
            image.save(temp_img_path)

            try:
                response = medical_agent.run(analysis_prompt, images=[temp_img_path])
                analysis_result = response.content

                with analysis_container:
                    st.markdown("### 📋 AI-Powered Medical Analysis")
                    st.markdown(analysis_result)

                # Save analysis result for chat & PDF
                st.session_state.last_analysis = analysis_result

            except Exception as e:
                st.error(f"Error during analysis: {e}")
            finally:
                os.remove(temp_img_path)

# Chat Section
if "last_analysis" in st.session_state:
    st.markdown("---")
    st.markdown("### 💬 Ask Follow-Up Questions")
    user_input = st.text_input("Ask something based on the analysis:", key="chat_input")

    if user_input and medical_agent:
        chat_query = f"{st.session_state.last_analysis}\n\nUser: {user_input}"
        with st.spinner("AI is replying..."):
            try:
                follow_up = medical_agent.run(chat_query)
                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", follow_up.content))
            except Exception as e:
                st.error(f"Chat error: {e}")

    for speaker, msg in st.session_state.chat_history[-6:]:
        st.chat_message(speaker).markdown(msg)

# Export to PDF using reportlab
if "last_analysis" in st.session_state:
    st.markdown("---")
    if st.button("📄 Export Analysis to PDF"):
        pdf_path = os.path.join(tempfile.gettempdir(), "diagnosis_report.pdf")
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", 12)

        y = height - 40
        for line in st.session_state.last_analysis.splitlines():
            if y < 60:
                c.showPage()
                y = height - 40
                c.setFont("Helvetica", 12)
            c.drawString(40, y, line.strip())
            y -= 18

        c.save()
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download PDF Report",
                data=f,
                file_name="diagnosis_report.pdf",
                mime="application/pdf"
            )

