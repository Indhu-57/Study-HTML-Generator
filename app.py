import streamlit as st
from supabase import create_client

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="ILM Generator",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------------------------
# Connect to Supabase
# --------------------------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("🎓 ILM Generator")
st.caption("AI-Powered Interactive Learning Material Generator")

st.write(
    "Generate interactive learning materials from **PDF, DOCX, and TXT** files using AI."
)

st.divider()

# --------------------------------------------------
# Course Information
# --------------------------------------------------
st.subheader("Course Information")

instructor = st.text_input(
    "Course Instructor",
    placeholder="e.g., Mrs. Indhumathi T"
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

# --------------------------------------------------
# Upload Files
# --------------------------------------------------
study_file = st.file_uploader(
    "Upload PDF / DOCX / TXT",
    type=["pdf", "docx", "txt"]
)

esign = st.file_uploader(
    "Upload E-Signature",
    type=["png", "jpg", "jpeg"]
)

st.divider()

# --------------------------------------------------
# Generate Button
# --------------------------------------------------
if st.button("🚀 Generate HTML"):

    # Basic validation
    if not instructor:
        st.error("Please enter the Course Instructor.")
        st.stop()

    if not department:
        st.error("Please enter the Department.")
        st.stop()

    if not programme:
        st.error("Please enter the Programme.")
        st.stop()

    if not subject:
        st.error("Please enter the Subject.")
        st.stop()

    if not topic:
        st.error("Please enter the Topic.")
        st.stop()

    if study_file is None:
        st.error("Please upload a study material.")
        st.stop()

    if esign is None:
        st.error("Please upload an E-Signature.")
        st.stop()

    try:

        response = supabase.table("generation_jobs").insert({

            "status": "Pending",
            "instructor": instructor,
            "department": department,
            "programme": programme,
            "subject": subject,
            "topic": topic

        }).execute()

        job_id = response.data[0]["id"]

# ----------------------------------------
# Upload Study Material
# ----------------------------------------

extension = study_file.name.split(".")[-1]

storage_path = f"{job_id}.{extension}"

supabase.storage.from_("AMP").upload(
    path=storage_path,
    file=study_file.getvalue(),
    file_options={
        "content-type": study_file.type
    }
)

st.success("✅ Study Material Uploaded!")

st.info(f"Job ID: {job_id}")

    except Exception as e:

        st.error("Database Error")
        st.exception(e)
