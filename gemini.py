import json
import time

import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import ServerError

# ==========================================
# GEMINI CLIENT
# ==========================================
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 8  # doubles each retry: 8s, 16s, 32s


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

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=final_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    max_output_tokens=65536,
                )
            )

            if not response.text:
                raise ValueError(
                    "Gemini returned an empty response. This can happen if the "
                    "output was cut off — try uploading fewer pages at once."
                )

            return json.loads(response.text)

        except ServerError as e:
            last_error = e
            is_overloaded = getattr(e, "code", None) == 503 or "UNAVAILABLE" in str(e)
            if is_overloaded and attempt < MAX_RETRIES:
                wait_seconds = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                st.warning(
                    f"Gemini is experiencing high demand (attempt {attempt}/{MAX_RETRIES}). "
                    f"Retrying in {wait_seconds} seconds..."
                )
                time.sleep(wait_seconds)
                continue
            raise

    raise last_error
