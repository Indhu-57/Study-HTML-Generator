import streamlit as st
from supabase import create_client

from storage import upload_file, save_uploaded_file
from extract import extract_text
from gemini import generate_learning_material, SUPPORTED_LANGUAGES
from html_generator import generate_html

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="ILM Generator",
    page_icon="🎓",
    layout="wide"
)

# =====================================================
# THEME - light blue background, light green input boxes
# with dark brown text inside, dark blue body text, and a
# dark brown title. Also tightens vertical spacing so the
# form fits on one screen as much as possible.
# =====================================================

st.markdown("""
<style>
:root {
    --ilm-bg: #d7ebf8;
    --ilm-box-bg: #dcf3df;
    --ilm-select-bg: #fbe0b8;
    --ilm-btn-bg: #f9d4dc;
    --ilm-box-text: #4a2f1f;
    --ilm-text: #123a6b;
    --ilm-title: #5c3a22;
}

.stApp {
    background-color: var(--ilm-bg);
}

/* Tighten overall vertical spacing so the page fits on one screen */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1.5rem !important;
}
div[data-testid="stVerticalBlock"] > div {
    gap: 0.4rem;
}
hr {
    margin: 0.6rem 0 !important;
}

/* Title */
h1 {
    color: var(--ilm-title) !important;
    font-weight: 800 !important;
    margin-bottom: 0.1rem !important;
}
h2, h3, .stSubheader {
    color: var(--ilm-title) !important;
}

/* All other body text (captions, paragraphs, labels) in dark blue */
.stApp, .stApp p, .stApp span, .stApp label,
[data-testid="stCaptionContainer"], .stMarkdown {
    color: var(--ilm-text) !important;
}

/* Input boxes: light green background, dark brown text */
.stTextInput input {
    background-color: var(--ilm-box-bg) !important;
    color: var(--ilm-box-text) !important;
    border: 1.5px solid #b7ddbe !important;
    border-radius: 8px !important;
    font-size: 0.95rem !important;
}
.stTextInput input::placeholder {
    color: var(--ilm-box-text) !important;
    opacity: 0.65 !important;
}

/* Select / dropdown boxes: light orange, including the popup list that
   opens when clicked (rendered by baseweb, needs its own selectors) */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--ilm-select-bg) !important;
    color: var(--ilm-box-text) !important;
    border: 1.5px solid #f0c896 !important;
    border-radius: 8px !important;
    font-size: 0.95rem !important;
}
.stSelectbox div[data-baseweb="select"] span,
.stSelectbox div[data-baseweb="select"] svg {
    color: var(--ilm-box-text) !important;
}
div[data-baseweb="popover"] ul[role="listbox"],
div[data-baseweb="popover"] li {
    background-color: var(--ilm-select-bg) !important;
    color: var(--ilm-box-text) !important;
}
div[data-baseweb="popover"] li:hover {
    background-color: #f5d9ae !important;
}

/* File uploader: full-width, same light green box family */
[data-testid="stFileUploaderDropzone"] {
    background-color: var(--ilm-box-bg) !important;
    border: 2px dashed #b7ddbe !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {
    color: var(--ilm-box-text) !important;
}

/* Buttons */
.stButton button, .stDownloadButton button {
    background-color: var(--ilm-btn-bg) !important;
    color: var(--ilm-box-text) !important;
    border: 1.5px solid #f0c5cd !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton button:hover, .stDownloadButton button:hover {
    background-color: #f5c9d3 !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SUPABASE CONNECTION
# =====================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =====================================================
# TITLE
# =====================================================

st.title("🎓 ILM Generator")
st.caption("AI Powered Interactive Learning Material System")

st.write("""
Generate interactive learning materials from **PDF, DOCX and TXT**
using Artificial Intelligence.
""")

st.divider()

# =====================================================
# COURSE INFORMATION (two-column layout)
# =====================================================

st.subheader("Course Information")

col1, col2 = st.columns(2)

with col1:
    instructor = st.text_input(
        "Course Instructor",
        placeholder="e.g. Mrs Indhumathi T"
    )
    programme = st.text_input(
        "Programme",
        placeholder="e.g. B.Sc. Mathematics"
    )
    topic = st.text_input(
        "Topic",
        placeholder="e.g. Travelling Salesman Problem"
    )

with col2:
    department = st.text_input(
        "Department",
        placeholder="e.g. Mathematics"
    )
    subject = st.text_input(
        "Subject",
        placeholder="e.g. Operations Research"
    )
    language = st.selectbox(
        "Output Language",
        SUPPORTED_LANGUAGES,
        index=0,
        help="The generated study material will be written in this language."
    )

# =====================================================
# FILE UPLOAD (full width, single column)
# =====================================================

study_file = st.file_uploader(
    "Upload Study Material",
    type=["pdf", "docx", "txt"]
)

st.divider()

# =====================================================
# GENERATE BUTTON
# =====================================================

if st.button("🚀 Generate Interactive Learning Material"):

    if not instructor:
        st.error("Please enter Course Instructor.")
        st.stop()

    if not department:
        st.error("Please enter Department.")
        st.stop()

    if not programme:
        st.error("Please enter Programme.")
        st.stop()

    if not subject:
        st.error("Please enter Subject.")
        st.stop()

    if not topic:
        st.error("Please enter Topic.")
        st.stop()

    if study_file is None:
        st.error("Please upload Study Material.")
        st.stop()

    try:

        with st.spinner("Creating generation job..."):

            response = supabase.table(
                "generation_jobs"
            ).insert({

                "status": "Processing",
                "instructor": instructor,
                "department": department,
                "programme": programme,
                "subject": subject,
                "topic": topic

            }).execute()

            job_id = response.data[0]["id"]

        st.success("Generation Job Created")

        # ===========================================
        # Upload Study Material
        # ===========================================

        study_path = upload_file(
            study_file,
            "study_materials",
            job_id
        )

        save_uploaded_file(
            job_id=job_id,
            file_name=study_file.name,
            storage_path=study_path,
            file_type="Study Material"
        )

        st.success("Files Uploaded Successfully")

        # ===========================================
        # Extract Text
        # (dispatches to the right extractor for PDF / DOCX / TXT
        # based on the file's extension, instead of assuming PDF)
        # ===========================================

        try:
            extracted_text, _page_count = extract_text(
                study_file.getvalue(),
                study_file.name
            )
        except ValueError as e:
            st.error(str(e))
            st.stop()

        if not extracted_text or not extracted_text.strip():
            st.error(
                "No text could be extracted from this file. It may be "
                "empty, corrupted, or an unsupported format."
            )
            st.stop()

        st.success("Text Extracted Successfully")

        with st.expander("Preview Extracted Text"):

            st.text_area(
                "",
                extracted_text[:3000],
                height=300
            )

        # ===========================================
        # Generate Learning Material using Gemini
        # ===========================================

        with st.spinner("Generating Learning Material using Gemini..."):

            result = generate_learning_material(
                extracted_text,
                language
            )

        st.success("Gemini Response Generated Successfully")

        # ===========================================
        # Fill Metadata
        # ===========================================

        if "metadata" not in result:
            result["metadata"] = {}

        result["metadata"]["topic"] = topic
        result["metadata"]["department"] = department
        result["metadata"]["programme"] = programme
        result["metadata"]["course_instructor"] = instructor
        result["metadata"]["subject"] = subject
        result["metadata"]["generated_on"] = ""

        # ===========================================
        # Generate HTML
        # ===========================================

        with st.spinner("Generating Interactive HTML..."):

            html = generate_html(result)

        st.success("Interactive HTML Generated Successfully")

        # ===========================================
        # Download Button
        # ===========================================

        st.download_button(
            label="📥 Download Interactive Learning Material",
            data=html,
            file_name=f"{topic.replace(' ','_')}.html",
            mime="text/html"
        )

        # ===========================================
        # Update Job Status
        # ===========================================

        supabase.table(
            "generation_jobs"
        ).update({

            "status": "Completed"

        }).eq(

            "id",
            job_id

        ).execute()

        st.success("🎉 ILM Generation Completed Successfully!")

    except Exception as e:

        if 'job_id' in locals():

            try:

                supabase.table(
                    "generation_jobs"
                ).update({

                    "status": "Failed"

                }).eq(

                    "id",
                    job_id

                ).execute()

            except:
                pass

        st.error("Something went wrong.")

        st.exception(e)
