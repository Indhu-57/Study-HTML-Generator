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
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 8  # doubles each retry: 8s, 16s, 32s, 64s, 128s

# ==========================================
# SUPPORTED OUTPUT LANGUAGES
# ==========================================
# Shown in the app's language dropdown. Add/remove entries here to change
# what's offered - no other code needs to change.
SUPPORTED_LANGUAGES = [
    "English",
    "Tamil",
    "Hindi",
    "Sanskrit",
    "Telugu",
    "Kannada",
    "Malayalam",
    "Bengali",
    "Marathi",
    "Gujarati",
    "Punjabi",
    "Urdu",
]

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


def _language_instruction(language):
    """
    Builds the block that tells Gemini which language to write the
    generated content in, while making sure the JSON structure itself
    (field names) is never translated - html_generator.py depends on
    exact English key names like "definitions", "mcqs", "steps", etc.
    """
    if not language or language.strip().lower() == "english":
        return ""  # default behaviour, no extra instruction needed

    return """
====================================================
OUTPUT LANGUAGE
Write ALL generated text content in {lang}. This applies to every
text field in the JSON: introduction, learning_outcomes, definitions
(term/meaning/examples), formulae (formula_name/explanation), worked_examples
(title/problem/steps/solution), important_notes, summary, practice_problems
(problem/answer), and mcqs (question/options/explanation).

Do NOT translate the JSON field/key names themselves (e.g. "introduction",
"definitions", "term", "meaning", "steps", "mcqs", "correct_answer", etc.)
- those must stay exactly as given in the schema, in English, so the JSON
can still be parsed correctly. Only the text VALUES should be in {lang}.

Mathematical/scientific notation - numbers, operators, symbols such as
+, -, =, ^, %, and formula variable names (like x, y, A, B) - should stay
in standard international notation even when the surrounding explanation
is in {lang}. The "correct_answer" field for MCQs must still be exactly
one of the letters A, B, C, or D, regardless of language.
====================================================
""".format(lang=language)


# ==========================================
# GENERATE LEARNING MATERIAL
# ==========================================
def generate_learning_material(extracted_text, language="English"):
    prompt = load_prompt()
    schema = load_schema()
    language_block = _language_instruction(language)
    final_prompt = f"""
{prompt}
{language_block}
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
                    "output was cut off - try uploading fewer pages at once."
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
