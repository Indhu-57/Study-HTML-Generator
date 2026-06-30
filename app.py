import streamlit as st

from supabase import create_client
import uuid

st.set_page_config(
    page_title="ILM Generator",
    page_icon="🎓",
    layout="wide"
)
# -----------------------------
# Supabase Connection
# -----------------------------
SUPABASE_URL = st.secrets["https://rminajhgtossrdguchks.supabase.co"]
SUPABASE_KEY = st.secrets["sb_publishable_qlbKijkbS52ZWuY2RuShvA_YBJ77SIr"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
st.title("🎓 ILM Generator")
st.caption("AI-Powered Interactive Learning Material Generator")

st.markdown("""
Generate interactive learning materials from **PDF, DOCX, and TXT** files using AI.
The generated content includes definitions, formulae, worked examples, important notes,
summaries, quizzes, flashcards, and an interactive HTML learning page.
""")

st.markdown("---")

st.subheader("Course Information")

instructor = st.text_input(
    "Course Instructor",
    placeholder="e.g., Mrs Indhumathi T"
)

department = st.text_input(
    "Department",
    placeholder="e.g., Mathematics"
)

programme = st.text_input(
    "Programme",
    placeholder="e.g., B.Sc. Mathematics"
)

subject = st.text_input(
    "Subject",
    placeholder="e.g., Operations Research"
)

topic = st.text_input(
    "Topic",
    placeholder="e.g., Travelling Salesman Problem"
)

study_file = st.file_uploader(
    "Upload PDF / DOCX / TXT",
    type=["pdf", "docx", "txt"]
)

esign = st.file_uploader(
    "Upload E-Signature",
    type=["png", "jpg", "jpeg"]
)

if st.button("Generate HTML"):
    st.success("Application is working! 🎉")
