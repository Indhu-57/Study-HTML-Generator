import streamlit as st
from google import genai

# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# ==========================================
# GENERATE JSON
# ==========================================

def generate_learning_material(extracted_text):

    prompt = f"""
You are an expert university professor and instructional designer.

Your task is to create high-quality Interactive Learning Material (ILM).

Study the following content carefully and generate educational material.

Rules:

1. Explain concepts clearly.
2. Use simple academic English.
3. Preserve technical correctness.
4. Do NOT invent facts.
5. Generate only information supported by the study material.
6. If a section is not applicable (for example Formulae), return an empty list.
7. Return ONLY valid JSON.
8. Do not include markdown.
9. Do not include ```json.
10. Do not include explanations outside JSON.

Study Material:

{extracted_text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
