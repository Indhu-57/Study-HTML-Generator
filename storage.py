import streamlit as st
from supabase import create_client

# ---------------------------------------------------
# Connect to Supabase
# ---------------------------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ---------------------------------------------------
# Upload File
# ---------------------------------------------------
def upload_file(file, folder, job_id):

    extension = file.name.split(".")[-1]

    storage_path = f"{folder}/{job_id}.{extension}"

    supabase.storage.from_("AMP").upload(
        path=storage_path,
        file=file.getvalue(),
        file_options={
            "content-type": file.type
        }
    )

    return storage_path


# ---------------------------------------------------
# Save Upload Details
# ---------------------------------------------------
def save_uploaded_file(
    job_id,
    file_name,
    storage_path,
    file_type
):

    supabase.table("uploaded_files").insert({

        "job_id": job_id,
        "file_name": file_name,
        "storage_path": storage_path,
        "file_type": file_type

    }).execute()
