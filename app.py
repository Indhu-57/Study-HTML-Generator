import streamlit as st
from supabase import create_client

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

st.markdown("""
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

    # -------------------------
    # Validation
    # -------------------------
    if instructor == "":
        st.error("Please enter Course Instructor.")
        st.stop()

    if department == "":
        st.error("Please enter Department.")
        st.stop()

    if programme == "":
        st.error("Please enter Programme.")
        st.stop()

    if subject == "":
        st.error("Please enter Subject.")
        st.stop()

    if topic == "":
        st.error("Please enter Topic.")
        st.stop()

    if study_file is None:
        st.error("Please upload the Study Material.")
        st.stop()

    if esign is None:
        st.error("Please upload the E-Signature.")
        st.stop()

    try:

        # ==========================================
        # Create Generation Job
        # ==========================================
        response = supabase.table("generation_jobs").insert({

            "status": "Pending",
            "instructor": instructor,
            "department": department,
            "programme": programme,
            "subject": subject,
            "topic": topic

        }).execute()

        job_id = response.data[0]["id"]

        # ==========================================
        # Upload Study Material
        # ==========================================
        extension = study_file.name.split(".")[-1]

        storage_path = f"study_materials/{job_id}.{extension}"

        supabase.storage.from_("AMP").upload(
            path=storage_path,
            file=study_file.getvalue(),
            file_options={
                "content-type": study_file.type
            }
        )

        # ==========================================
        # SUCCESS
        # ==========================================
        st.success("✅ Generation Job Created Successfully!")
        st.success("✅ Study Material Uploaded Successfully!")

        st.info(f"Job ID: {job_id}")

    except Exception as e:

        st.error("Something went wrong.")
        st.exception(e)
