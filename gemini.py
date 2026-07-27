import json
import re
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
# Gemini's raw JSON response occasionally has one of a few common LLM
# mistakes that make it fail strict json.loads() even though the content
# itself is fine. Each of these is repaired independently, and every
# combination of them is tried before giving up, since a single response
# can have more than one issue at once.
#
# 1. Invalid backslash escapes - most often from math notation
#    (\alpha, \frac{1}{2}), regex patterns (\d+), or file paths
#    (C:\Users) that were not doubled into \\ the way JSON requires.
#    Repaired by _repair_invalid_json_escapes.
#
# 2. Trailing commas before a closing } or ] (e.g. {"a": 1,} or
#    [1, 2,]) - valid in many languages but not in strict JSON. This is
#    the exact cause of a "Expecting property name enclosed in double
#    quotes" error pointing at the character right after the comma.
#    Repaired by _remove_trailing_commas.
#
# 3. A literal (unescaped) newline/tab character inside a string value,
#    instead of the required \n / \t escape sequence. Rather than trying
#    to locate and fix these one at a time, we simply also try parsing
#    with json.loads(..., strict=False), which permits raw control
#    characters inside strings.
#
# None of these change already-valid JSON, so a clean response is
# unaffected either way.

# Note: \b (backspace) and \f (formfeed) are deliberately NOT treated as
# "safe, leave alone" escapes here, even though they are technically
# valid JSON escapes - study material never intentionally contains a
# literal backspace/formfeed character, but frequently contains
# unescaped math notation that starts with those letters (\beta, \frac,
# \forall). Treating \b / \f as already-valid would silently corrupt
# that text instead of fixing it.
_SAFE_JSON_ESCAPES = set('"\\/nrtu')

# Matches a comma, followed only by whitespace, immediately before a
# closing } or ] - i.e. a trailing comma with nothing meaningful after it.
_TRAILING_COMMA_RE = re.compile(r',(\s*[}\]])')


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


def _remove_trailing_commas(text):
    """Removes a comma that appears right before a closing } or ], e.g.
    {"a": 1,} -> {"a": 1} or [1, 2,] -> [1, 2]. A no-op on JSON that
    doesn't have this problem."""
    return _TRAILING_COMMA_RE.sub(r'\1', text)


def _parse_gemini_json(raw_text):
    """
    Parses Gemini's JSON response, trying several repair strategies (and
    every combination of them) if the plain parse fails, since a single
    response can have more than one of these common LLM JSON mistakes at
    once:
      - invalid backslash escapes (math notation, regex, file paths)
      - trailing commas before a closing } or ]
      - a literal newline/tab inside a string value instead of \\n / \\t

    Raises the ORIGINAL JSONDecodeError (not a repair attempt's) if
    nothing works, so the real problem is still visible in the traceback.
    """
    candidates = [raw_text]

    escaped = _repair_invalid_json_escapes(raw_text)
    if escaped != raw_text:
        candidates.append(escaped)

    no_trailing_commas = _remove_trailing_commas(raw_text)
    if no_trailing_commas != raw_text:
        candidates.append(no_trailing_commas)

    escaped_no_commas = _remove_trailing_commas(escaped)
    if escaped_no_commas not in candidates:
        candidates.append(escaped_no_commas)

    first_error = None
    for candidate in candidates:
        for strict in (True, False):
            try:
                return json.loads(candidate, strict=strict)
            except json.JSONDecodeError as e:
                if first_error is None:
                    first_error = e
                continue

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
