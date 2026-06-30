import streamlit as st

st.set_page_config(
    page_title="AI Study HTML Generator",
    layout="wide"
)

st.title("📚 AI Interactive Study HTML Generator")

st.markdown("---")

st.subheader("Course Information")

col1, col2 = st.columns(2)

with col1:
    instructor = st.text_input("Course Instructor")

    department = st.text_input("Department")

    programme = st.text_input("Programme")

with col2:
    subject = st.text_input("Subject")

    topic = st.text_input("Topic")

st.markdown("---")

st.subheader("Upload Files")

study_file = st.file_uploader(
    "Upload PDF / DOCX / TXT",
    type=["pdf", "docx", "txt"]
)

esign = st.file_uploader(
    "Upload E-Signature",
    type=["png", "jpg", "jpeg"]
)

st.markdown("---")

st.subheader("Generate Content")

definitions = st.checkbox("Definitions", value=True)
formulae = st.checkbox("Formulae", value=True)
examples = st.checkbox("Worked Examples", value=True)
notes = st.checkbox("Important Notes", value=True)
summary = st.checkbox("Summary", value=True)
mcqs = st.checkbox("MCQs", value=True)
flashcards = st.checkbox("Flashcards", value=True)
shortq = st.checkbox("Short Questions", value=True)
longq = st.checkbox("Long Questions", value=True)
mindmap = st.checkbox("Mind Map", value=True)

mcq_count = st.number_input(
    "Number of MCQs",
    min_value=5,
    max_value=100,
    value=20
)

difficulty = st.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard", "Mixed"]
)

st.markdown("---")

if st.button("🚀 Generate HTML"):

    if study_file is None:
        st.error("Please upload a study file.")
    else:
        st.success("Everything looks good!")
        st.info("Next step: Uploading file to Supabase...")
