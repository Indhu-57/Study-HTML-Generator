import json
import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# GEMINI CLIENT
# ==========================================
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ==========================================
# LOAD PROMPT
# ==========================================
def load_prompt():
    with open("prompts/ilm_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()


# ==========================================
# LOAD JSON SCHEMA
# ==========================================
def load_schema():
    with open("schemas/schema.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================================
# GENERATE LEARNING MATERIAL
# ==========================================
def generate_learning_material(extracted_text):
    prompt = load_prompt()
    schema = load_schema()
    final_prompt = f"""
{prompt}
====================================================
The generated JSON MUST follow this schema:
{json.dumps(schema, indent=2)}
====================================================
Study Material
{extracted_text}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=final_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            # Large (up to ~200 page) uploads produce a lot of definitions,
            # examples, and MCQs — raise the output ceiling so the JSON
            # doesn't get cut off mid-response and fail to parse.
            max_output_tokens=65536,
        )
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response. This can happen if the "
            "output was cut off — try uploading fewer pages at once."
        )

    return json.loads(response.text)
