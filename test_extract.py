import streamlit as st
from extract import extract_pdf_text

st.set_page_config(page_title="PDF Extraction Test")

st.title("📄 PDF Text Extraction Test")

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    with st.spinner("Extracting text..."):

        text = extract_pdf_text(uploaded_file.getvalue())

    st.success("Text extracted successfully!")

    st.write(f"Characters extracted: {len(text)}")

    st.text_area(
        "Extracted Text",
        text,
        height=500
    )
