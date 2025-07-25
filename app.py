import streamlit as st

# Must be first!
st.set_page_config(page_title="Cursive.ai", page_icon="✍️", layout="centered")
st.markdown("""
    <style>
    /* Gradient Background */
    body {
        background: linear-gradient(to right, #7F00FF, #00C9FF);
    }
    .stApp {
        background: linear-gradient(to right, #7F00FF, #00C9FF);
    }
    .block-container {
        max-width: 800px;
        margin: auto;
        padding-top: 2rem;
    }
    /* Headings Glow */
    h1 {
        font-size: 3rem;
        color: white;
        text-align: center;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.7), 0 0 20px rgba(255, 255, 255, 0.5);
    }
    h2, h3 {
        color: white;
        text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
    }
    /* Card-like Boxes */
    .stTextInput, .stFileUploader, .stTextArea, .stButton {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px;
        color: white;
    }
    textarea, input {
        color: white !important;
    }
    .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

import os
import spacy
import language_tool_python
from ocr import (
    authenticate_google,
    upload_image_and_convert_to_doc,
    extract_text_from_doc,
    clean_and_correct_text
)
from text_processing import load_summarizer, load_sentiment_analyzer, summarize_text, analyze_sentiment, extract_keywords_with_google_links

# Load spaCy + grammar tool
nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool("en-US")

# File saving
def save_uploaded_file(uploaded_file):
    save_path = os.path.join("uploaded_images", uploaded_file.name)
    os.makedirs("uploaded_images", exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

@st.cache_resource
def get_google_creds():
    return authenticate_google()

# Header
st.markdown("<h1 style='text-align: center;'>✍️ Cursive.ai</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Handwriting ➡️ Clean Text ➡️ Summarize ➡️ Keywords</h4>", unsafe_allow_html=True)
st.markdown("---")

# Glass Card Start
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

# Upload Section
uploaded_file = st.file_uploader("📤 Upload a handwritten image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.success("✅ Image uploaded successfully!")
    st.image(uploaded_file, caption="📄 Uploaded Handwritten Image", use_container_width=True)

    local_image_path = save_uploaded_file(uploaded_file)

    creds = get_google_creds()
    if isinstance(creds, str):
        st.error(creds)
    else:
        with st.spinner('🔄 Extracting text... please wait...'):
            doc_id = upload_image_and_convert_to_doc(local_image_path, creds)
            if isinstance(doc_id, str) and "Error" in doc_id:
                st.error(doc_id)
            else:
                extracted_text = extract_text_from_doc(doc_id, creds)
                if isinstance(extracted_text, str) and "Error" in extracted_text:
                    st.error(extracted_text)
                else:
                    formatted_text = clean_and_correct_text(extracted_text)

                    st.markdown("### 📜 Extracted & Corrected Text")
                    st.text_area("Formatted Output:", formatted_text, height=300)

                    text_file = "formatted_text.txt"
                    with open(text_file, "w", encoding="utf-8") as f:
                        f.write(formatted_text)

                    st.download_button(
                        label="📥 Download Text File",
                        data=open(text_file, "r", encoding="utf-8").read(),
                        file_name="formatted_text.txt",
                        mime="text/plain"
                    )

                    st.markdown("---")
                    st.markdown("### ✨ Enhance Extracted Text")

                    summarizer = load_summarizer()
                    sentiment_analyzer = load_sentiment_analyzer()

                    with st.expander("📝 Summarize Text"):
                        if st.button("Generate Summary"):
                            with st.spinner('✍️ Summarizing...'):
                                summary = summarize_text(formatted_text, summarizer)
                                st.success(summary)

                    with st.expander("💬 Analyze Sentiment"):
                        if st.button("Analyze"):
                            with st.spinner('🔍 Analyzing sentiment...'):
                                sentiment_label, sentiment_score = analyze_sentiment(formatted_text, sentiment_analyzer)
                                st.info(f"**Sentiment:** {sentiment_label}  (Score: {sentiment_score:.2f})")

                    with st.expander("🔑 Extract Keywords + Google Links"):
                        if st.button("Extract Keywords"):
                            with st.spinner('🔎 Extracting keywords...'):
                                keywords_with_links = extract_keywords_with_google_links(formatted_text)
                                st.markdown("#### 🔎 Click below to search:")
                                for kw, link in keywords_with_links.items():
                                    st.markdown(
                                        f"<a href='{link}' target='_blank' class='keyword-btn'>{kw}</a>",
                                        unsafe_allow_html=True
                                    )

    # Cleanup
    if os.path.exists(local_image_path):
        os.remove(local_image_path)

else:
    st.info("👆 Please upload an image to start!")

# Glass Card End
st.markdown('</div>', unsafe_allow_html=True)
