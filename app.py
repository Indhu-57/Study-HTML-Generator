import streamlit as st

st.set_page_config(
    page_title="AI Study HTML Generator",
    layout="wide"
)

st.title("📚 AI Interactive Study HTML Generator")

st.write("Welcome! Your application is now running on Streamlit Community Cloud.")

st.header("Course Information")

instructor = st.text_input("Course Instructor")
department = st.text_input("Department")
programme = st.text_input("Programme")
subject = st.text_input("Subject")
topic = st.text_input("Topic")

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
