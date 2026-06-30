import streamlit as st

st.set_page_config(
    page_title="ILM Generator",
    page_icon="🎓",
    layout="wide"
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
