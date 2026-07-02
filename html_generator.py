from pathlib import Path


def generate_html(data):

    css = Path("assets/style.css").read_text(encoding="utf-8")
    js = Path("assets/script.js").read_text(encoding="utf-8")

    metadata = data.get("metadata", {})

    html = f"""
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{metadata.get("topic","ILM Generator")}</title>

<style>

{css}

</style>

</head>

<body>

<div class="container">

<header>

<h1>{metadata.get("topic","")}</h1>

<h2>AI Powered Interactive Learning Material</h2>

</header>

<div class="info-card">

<p><strong>Instructor:</strong> {metadata.get("course_instructor","")}</p>

<p><strong>Department:</strong> {metadata.get("department","")}</p>

<p><strong>Programme:</strong> {metadata.get("programme","")}</p>

<p><strong>Subject:</strong> {metadata.get("subject","")}</p>

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

<button onclick="toggleFlashcard('flash{i}')">

Show Answer

</button>

<div id="flash{i}" style="display:none; margin-top:10px;">

{flashcard.get("answer","")}

</div>

</div>
"""

    html += """
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

<button onclick="checkAnswer('q{i}','{mcq.get("correct_answer","")}')">

Check Answer

</button>

<p id="q{i}_result"></p>

<p><strong>Explanation:</strong> {mcq.get("explanation","")}</p>

</div>
"""

    html += f"""

<footer>

<h2>ILM Generator</h2>

<p><strong>AI Powered Interactive Learning Material System</strong></p>

<br>

<p>Designed by</p>

<h3>Mrs Indhumathi T</h3>

<p>Research Scholar</p>

<p>Department of Mathematics</p>

<p>SCSVMV (Deemed to be University), Kanchipuram</p>

<br>

<p>© 2026 All Rights Reserved</p>

</footer>

</div>

<script>

{js}

</script>

</body>

</html>
"""

    return html
