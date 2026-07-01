import json
import streamlit as st
from google import genai

# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# ==========================================
# LOAD MASTER PROMPT
# ==========================================

def load_prompt():

    with open("prompts/ilm_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


# ==========================================
# GENERATE LEARNING MATERIAL
# ==========================================

def generate_learning_material(extracted_text):

    master_prompt = load_prompt()

    final_prompt = f"""
{master_prompt}

==================================================

STUDY MATERIAL

==================================================

{extracted_text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=final_prompt
    )

    return response.text
