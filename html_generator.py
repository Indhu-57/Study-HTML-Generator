import base64
from datetime import datetime
from pathlib import Path


def _load_logo_base64():
    """
    Looks for a college logo at assets/logo.png (or .jpg/.jpeg).
    Returns a base64 data-URI string, or None if no logo file exists yet.
    This keeps the generator safe even before a logo is uploaded to the repo.
    """
    for filename in ("logo.png", "logo.jpg", "logo.jpeg"):
        path = Path("assets") / filename
        if path.exists():
            ext = path.suffix.lstrip(".").lower()
            mime = "jpeg" if ext in ("jpg", "jpeg") else "png"
            encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
            return f"data:image/{mime};base64,{encoded}"
    return None


def generate_html(data):
    css = Path("assets/style.css").read_text(encoding="utf-8")
    js = Path("assets/script.js").read_text(encoding="utf-8")

    metadata = data.get("metadata", {})
    topic = metadata.get("topic", "")
    instructor = metadata.get("course_instructor", "")
    department = metadata.get("department", "")
    programme = metadata.get("programme", "")
    subject = metadata.get("subject", "")
    generated_on = metadata.get("generated_on") or datetime.now().strftime("%d %B %Y")

    logo_data_uri = _load_logo_base64()

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{topic or "Interactive Learning Material"}</title>
<style>
{css}
</style>
</head>
<body>
<div class="container">

<header>
<h1>{topic}</h1>
</header>

<div class="info-card">
<p><strong>Course Instructor:</strong> {instructor}</p>
<p><strong>Department:</strong> {department}</p>
<p><strong>Programme:</strong> {programme}</p>
<p><strong>Subject:</strong> {subject}</p>
<p><strong>Generated on:</strong> {generated_on}</p>
</div>

<div class="section">
<h2>📖 Introduction</h2>
<p>{data.get("introduction","")}</p>
</div>

<div class="section">
<h2>🎯 Learning Outcomes</h2>
<ul>
"""
    for item in data.get("learning_outcomes", []):
        html += f"<li>{item}</li>"

    html += """
</ul>
</div>

<div class="section">
<h2>📚 Definitions</h2>
"""
    for definition in data.get("definitions", []):
        html += f"""
<div class="card">
<h3>{definition.get("term","")}</h3>
<p>{definition.get("meaning","")}</p>
</div>
"""

    html += """
</div>

<div class="section">
<h2>➗ Formulae</h2>
"""
    for formula in data.get("formulae", []):
        html += f"""
<div class="card formula-card">
<h3>{formula.get("formula_name","")}</h3>
<p class="formula">{formula.get("formula","")}</p>
<p>{formula.get("explanation","")}</p>
</div>
"""

    html += """
</div>

<div class="section">
<h2>✏️ Worked Examples</h2>
"""
    for i, example in enumerate(data.get("worked_examples", []), start=1):
        html += f"""
<div class="card example-card">
<h3>Example {i}: {example.get("title","")}</h3>
<p><strong>Problem:</strong> {example.get("problem","")}</p>
<ol>
"""
        for step in example.get("steps", []):
            html += f"<li>{step}</li>"
        html += f"""
</ol>
<p><strong>Answer:</strong> {example.get("solution","")}</p>
</div>
"""

    html += """
</div>

<div class="section">
<h2>💡 Important Notes</h2>
<ul>
"""
    for note in data.get("important_notes", []):
        html += f"<li>{note}</li>"

    html += """
</ul>
</div>

<div class="section">
<h2>📄 Summary</h2>
<ul>
"""
    for point in data.get("summary", []):
        html += f"<li>{point}</li>"

    html += """
</ul>
</div>

<div class="section">
<h2>🗂 Flashcards</h2>
"""
    for i, flashcard in enumerate(data.get("flashcards", []), start=1):
        html += f"""
<div class="flashcard">
<strong>Question:</strong>
<p>{flashcard.get("question","")}</p>
<button onclick="toggleFlashcard('flash{i}')">Show Answer</button>
<div id="flash{i}" style="display:none; margin-top:10px;">
{flashcard.get("answer","")}
</div>
</div>
"""

    html += """
</div>

<div class="section">
<h2>✅ Quiz</h2>
"""
    for i, mcq in enumerate(data.get("mcqs", []), start=1):
        html += f"""
<div class="mcq">
<p><strong>Q{i}. {mcq.get("question","")}</strong></p>
<label><input type="radio" name="q{i}" value="A"> {mcq.get("option_a","")}</label><br>
<label><input type="radio" name="q{i}" value="B"> {mcq.get("option_b","")}</label><br>
<label><input type="radio" name="q{i}" value="C"> {mcq.get("option_c","")}</label><br>
<label><input type="radio" name="q{i}" value="D"> {mcq.get("option_d","")}</label><br><br>
<button onclick="checkAnswer('q{i}','{mcq.get("correct_answer","")}')">Check Answer</button>
<p id="q{i}_result"></p>
<p><strong>Explanation:</strong> {mcq.get("explanation","")}</p>
</div>
"""

    html += """
</div>

<footer>
"""

    if logo_data_uri:
        html += f"""
<div class="logo-block">
<img src="{logo_data_uri}" alt="College Logo" class="college-logo">
</div>
"""

    html += f"""
<p class="designed-by-label">Designed by</p>
<h3>Mrs Indhumathi T</h3>
<p>Research Scholar</p>
<p>Department of Mathematics</p>
<p>SCSVMV (Deemed to be University), Kanchipuram</p>
<br>
<p>&copy; 2026 All Rights Reserved</p>
</footer>

</div>
<script>
{js}
</script>
</body>
</html>
"""
    return html
