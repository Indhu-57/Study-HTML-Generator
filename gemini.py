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
# JSON REPAIR
# ==========================================
# Gemini occasionally emits a raw backslash inside a JSON string value
# that is not a valid JSON escape sequence - most often from math
# notation (\alpha, \frac{1}{2}), regex patterns (\d+), or file paths
# (C:\Users) that it did not double into \\ the way JSON requires. That
# breaks json.loads with "Invalid \escape". This repairs it by scanning
# the raw response text and doubling any backslash that is not part of a
# genuine JSON escape, before parsing - and is a no-op on already-valid
# JSON, so it never changes a response that was fine to begin with.

# Note: \b (backspace) and \f (formfeed) are deliberately NOT treated as
# "safe, leave alone" escapes here, even though they are technically
# valid JSON escapes - study material never intentionally contains a
# literal backspace/formfeed character, but frequently contains
# unescaped math notation that starts with those letters (\beta, \frac,
# \forall). Treating \b / \f as already-valid would silently corrupt
# that text instead of fixing it.
_SAFE_JSON_ESCAPES = set('"\\/nrtu')


def _repair_invalid_json_escapes(text):
    """Doubles every backslash in `text` that is not part of a genuine
    JSON escape sequence (\\" \\\\ \\/ \\n \\r \\t \\uXXXX)."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue

        nxt = text[i + 1] if i + 1 < n else ""
        if nxt == "u" and i + 6 <= n and all(c in "0123456789abcdefABCDEF" for c in text[i + 2:i + 6]):
            out.append(text[i:i + 6])
            i += 6
        elif nxt in _SAFE_JSON_ESCAPES and nxt != "u":
            out.append(text[i:i + 2])
            i += 2
        else:
            out.append("\\\\")
            i += 1
    return "".join(out)


def _parse_gemini_json(raw_text):
    """
    Parses Gemini's JSON response, automatically repairing invalid
    backslash escapes if the first parse attempt fails. Raises the
    original JSONDecodeError (not the retry's) if repair doesn't help,
    so the real problem is still visible in the traceback.
    """
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as first_error:
        try:
            return json.loads(_repair_invalid_json_escapes(raw_text))
        except json.JSONDecodeError:
            raise first_error


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
            return _parse_gemini_json(response.text)
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
