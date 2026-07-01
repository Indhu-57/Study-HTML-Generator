import streamlit as st
from google import genai

# ---------------------------------------
# Configure Gemini Client
# ---------------------------------------

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# ---------------------------------------
# Generate Learning Material
# ---------------------------------------

def generate_learning_material(text):

    prompt = f"""
You are an expert university professor.

Read the study material below and explain it in simple academic English.

Study Material:

{text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
