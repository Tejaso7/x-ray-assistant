# Medical Imaging Diagnosis Agent

A Streamlit application that utilizes Google's Gemini AI to analyze and provide diagnostic insights for medical images, supported by web search capabilities.

https://x-ray-Agent.streamlit.app/

https://x-ray-chatbot.streamlit.app/
## Overview

This application allows healthcare professionals and users to upload medical images (X-ray, MRI, CT, Ultrasound, etc.) and receive a comprehensive AI-powered analysis. The agent provides structured insights including image type identification, key findings, diagnostic assessment, and patient-friendly explanations, all supported by recent medical literature through integrated web search.

## Features

- **AI-Powered Image Analysis**: Leverages Google's Gemini 2.0 Flash model for medical image interpretation
- **Structured Analysis Reports**: Provides organized insights with clear sections for findings and diagnoses
- **Research Integration**: Incorporates relevant medical literature through DuckDuckGo search
- **Patient-Friendly Explanations**: Translates complex medical findings into accessible language
- **Secure API Management**: Safely stores Google API keys in the session state

## Requirements

- Python 3.7+
- Google Gemini API key

## Installation

### Setting up a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate
```

### Installing Dependencies

```bash
# Install required packages from requirements.txt
pip install -r requirements.txt
```

### Project Structure

Ensure you have the following files in your project directory:
- `app.py` (the main application file)
- `static/iffort blue logo.png` (logo image file)
- `requirements.txt` (containing all necessary dependencies)

## Usage

1. Start the Streamlit application:

```bash
streamlit run app.py
```

2. Open your web browser and navigate to the local URL provided (typically http://localhost:8501)

3. In the sidebar, enter your Google API key from [Google AI Studio](https://aistudio.google.com/apikey)

4. Upload a medical image (supported formats: JPG, JPEG, PNG)

5. Click "Analyze Image" to receive a comprehensive analysis

## Analysis Output

The application provides a structured analysis with five key sections:

1. **Image Type & Region**: Identifies the imaging modality and anatomical region
2. **Key Findings**: Lists observations and abnormalities with precise descriptions
3. **Diagnostic Assessment**: Provides primary and differential diagnoses with confidence levels
4. **Patient-Friendly Explanation**: Explains findings in clear, accessible language
5. **Research Context**: Includes recent medical literature and relevant references

## Important Notes

- This tool is for educational and informational purposes only
- All analyses should be reviewed by qualified healthcare professionals
- Do not make medical decisions based solely on this analysis

## Security Considerations

- API keys are stored in the Streamlit session state and not persisted
- User-uploaded images are temporarily stored and then deleted after analysis
- No patient data is permanently stored by the application

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for providing the AI model
- [Streamlit](https://streamlit.io/) for the web application framework
- [Phi Framework](https://docs.philab.dev/) for agent development utilities
