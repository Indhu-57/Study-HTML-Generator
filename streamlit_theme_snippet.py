STREAMLIT_APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --ilm-red: #c96a5b;
    --ilm-red-dark: #a85142;
    --ilm-red-pale: #f6e3df;
    --ilm-sky: #7fb3d5;
    --ilm-sky-pale: #e3f0f7;
    --ilm-brown: #8b6f52;
    --ilm-brown-pale: #f2e9df;
    --ilm-text: #3a2f28;
    --ilm-bg: #fdf9f4;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--ilm-text);
}

.stApp {
    background: linear-gradient(160deg, var(--ilm-bg) 0%, var(--ilm-sky-pale) 45%, var(--ilm-red-pale) 100%);
    background-attachment: fixed;
}

/* Titles */
h1 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
    color: var(--ilm-red-dark) !important;
    letter-spacing: -0.3px;
}
h2, h3 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    color: var(--ilm-brown) !important;
}

/* Caption / subtitle under the main title */
.stApp [data-testid="stCaptionContainer"], .stCaption {
    color: var(--ilm-sky) !important;
    font-weight: 500;
}

/* "Course Information" style section as a soft formal card */
.stApp [data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffffcc;
    border: 1px solid var(--ilm-brown-pale);
    border-radius: 16px;
    padding: 8px 4px;
    box-shadow: 0 4px 18px rgba(139, 111, 82, 0.08);
}

/* Text inputs / select boxes */
.stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1.5px solid var(--ilm-brown-pale) !important;
    border-radius: 10px !important;
    color: var(--ilm-text) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within > div {
    border-color: var(--ilm-sky) !important;
    box-shadow: 0 0 0 3px rgba(127, 179, 213, 0.25) !important;
}

/* Labels above inputs */
.stTextInput label, .stSelectbox label, .stFileUploader label {
    color: var(--ilm-brown) !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
}

/* File uploader dropzone */
[data-testid="stFileUploaderDropzone"] {
    background-color: var(--ilm-sky-pale) !important;
    border: 2px dashed var(--ilm-sky) !important;
    border-radius: 14px !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background-color: #d7ebf5 !important;
}

/* Buttons */
.stButton button, .stDownloadButton button {
    background: linear-gradient(135deg, var(--ilm-red) 0%, var(--ilm-red-dark) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.6rem !important;
    box-shadow: 0 4px 14px rgba(201, 106, 91, 0.3);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton button:hover, .stDownloadButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(201, 106, 91, 0.4);
}

/* Dividers */
hr {
    border-color: var(--ilm-brown-pale) !important;
}

/* Expander (Preview Extracted Text, per-file summary, etc.) */
.streamlit-expanderHeader {
    background-color: var(--ilm-brown-pale) !important;
    border-radius: 10px !important;
    color: var(--ilm-brown) !important;
    font-weight: 600 !important;
}

/* Success / warning / error boxes - soften the default colors to match */
[data-testid="stNotification"] {
    border-radius: 12px !important;
}

/* Sticky top header bar Streamlit adds */
[data-testid="stHeader"] {
    background: transparent !important;
}
</style>
"""
