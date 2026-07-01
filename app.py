import streamlit as st
from supabase import create_client

from storage import upload_file, save_uploaded_file
from extract import extract_pdf_text

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="ILM Generator",
    page_icon="🎓",
    layout="wide"
)

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
st.caption("AI-Powered Interactive Learning Material Generator")

st.write("""
Generate interactive learning materials from **PDF, DOCX and TXT**
using Artificial Intelligence.
""")

st.divider()

# =====================================================
# COURSE INFORMATION
# =====================================================
st.subheader("Course Information")

instructor = st.text_input(
    "Course Instructor",
    placeholder="e.g., Indhumathi T"
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

# =====================================================
# FILE UPLOADS
# =====================================================
study_file = st.file_uploader(
    "Upload PDF / DOCX / TXT",
    type=["pdf", "docx", "txt"]
)

esign = st.file_uploader(
    "Upload E-Signature",
    type=["png", "jpg", "jpeg"]
)

st.divider()

# =====================================================
# GENERATE BUTTON
# =====================================================
if st.button("🚀 Generate HTML"):

    # -----------------------------
    # Validation
    # -----------------------------
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
        st.error("Please upload the Study Material.")
        st.stop()

    if esign is None:
        st.error("Please upload the E-Signature.")
        st.stop()

    try:

        # =====================================================
        # CREATE GENERATION JOB
        # =====================================================
        response = supabase.table("generation_jobs").insert({

            "status": "Pending",
            "instructor": instructor,
            "department": department,
            "programme": programme,
            "subject": subject,
            "topic": topic

        }).execute()

        job_id = response.data[0]["id"]

        # =====================================================
        # UPLOAD STUDY MATERIAL
        # =====================================================
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

        # =====================================================
        # UPLOAD SIGNATURE
        # =====================================================
        signature_path = upload_file(
            esign,
            "signatures",
            job_id
        )

        save_uploaded_file(
            job_id=job_id,
            file_name=esign.name,
            storage_path=signature_path,
            file_type="Signature"
        )

        # =====================================================
        # EXTRACT PDF TEXT
        # =====================================================
        if study_file.type == "application/pdf":

            extracted_text = extract_pdf_text(
                study_file.getvalue()
            )

            st.subheader("📄 Extracted Text Preview")

            st.text_area(
                "Preview (First 3000 Characters)",
                extracted_text[:3000],
                height=300
            )

        # =====================================================
        # SUCCESS
        # =====================================================
        st.success("✅ Generation Job Created Successfully!")
        st.success("✅ Study Material Uploaded Successfully!")
        st.success("✅ E-Signature Uploaded Successfully!")

        st.info(f"Job ID: {job_id}")

    except Exception as e:

        st.error("Something went wrong.")
        st.exception(e)
