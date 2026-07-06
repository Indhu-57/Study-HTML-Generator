import base64
import json
from datetime import datetime
from pathlib import Path


def _load_logo_base64():
    """
    Looks for a college logo at assets/logo.png (or .jpg/.jpeg).
    Returns a base64 data-URI string, or None if no logo file exists yet.
    """
    for filename in ("logo.png", "logo.jpg", "logo.jpeg"):
        path = Path("assets") / filename
        if path.exists():
            ext = path.suffix.lstrip(".").lower()
            mime = "jpeg" if ext in ("jpg", "jpeg") else "png"
            encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
            return f"data:image/{mime};base64,{encoded}"
    return None


def _initials(text, max_len=3):
    """Turns 'Quantitative Aptitude' into 'QA' for the nav badge."""
    if not text:
        return "ILM"
    words = [w for w in text.replace("&", " ").split() if w]
    letters = "".join(w[0].upper() for w in words[:max_len])
    return letters or text[:3].upper()


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
    badge_text = _initials(subject)

    # -----------------------------------------------------
    # STUDY PAGE — accordion sections built from the JSON
    # -----------------------------------------------------
    study_sections = []

    # Section 1: Introduction + Learning Outcomes
    intro_body = ""
    if data.get("introduction"):
        intro_body += f'<p style="margin-bottom:16px;">{data.get("introduction","")}</p>'
    if data.get("learning_outcomes"):
        intro_body += '<p style="font-weight:700;color:var(--navy);margin-bottom:8px;">🎯 Learning Outcomes</p>'
        intro_body += '<ul class="key-points">'
        for item in data.get("learning_outcomes", []):
            intro_body += f"<li>{item}</li>"
        intro_body += "</ul>"
    if intro_body:
        study_sections.append(("📖", "Introduction & Learning Outcomes", intro_body, True))

    # Section 2: Definitions
    if data.get("definitions"):
        body = ""
        for d in data.get("definitions", []):
            body += f'''
<div class="def-box">
<div class="def-title">{d.get("term","")} <span>Definition</span></div>
<p>{d.get("meaning","")}</p>
</div>
'''
        study_sections.append(("📚", "Definitions", body, True))

    # Section 3: Formulae + Worked Examples (kept together on the Study page too)
    if data.get("formulae") or data.get("worked_examples"):
        body = ""
        if data.get("formulae"):
            body += '<div class="formula-grid">'
            for f in data.get("formulae", []):
                body += f'''
<div class="formula-card">
<div class="f-label">{f.get("formula_name","")}</div>
<div class="f-eq">{f.get("formula","")}</div>
<div class="f-desc">{f.get("explanation","")}</div>
</div>
'''
            body += "</div>"
        for i, ex in enumerate(data.get("worked_examples", []), start=1):
            steps_html = "".join(f"<li>{s}</li>" for s in ex.get("steps", []))
            body += f'''
<div class="worked-example">
<div class="we-q">Example {i}: {ex.get("title","")} — {ex.get("problem","")}</div>
<div class="we-a"><ol>{steps_html}</ol><code>{ex.get("solution","")}</code></div>
</div>
'''
        study_sections.append(("➗", "Formulae & Worked Examples", body, False))

    # Section 4: Important Notes
    if data.get("important_notes"):
        body = '<div class="note-box"><strong>📝 Key Points:</strong><br>'
        body += " &nbsp;|&nbsp; ".join(data.get("important_notes", []))
        body += "</div>"
        study_sections.append(("💡", "Important Notes", body, False))

    # Section 5: Summary
    if data.get("summary"):
        summary_val = data.get("summary")
        body = '<ul class="summary-list">'
        if isinstance(summary_val, list):
            for point in summary_val:
                body += f"<li>{point}</li>"
        else:
            # Model returned a paragraph string instead of a list — show as-is
            body += f"<li>{summary_val}</li>"
        body += "</ul>"
        study_sections.append(("📄", "Summary", body, False))

    # Section 6: Flashcards
    if data.get("flashcards"):
        body = ""
        for i, card in enumerate(data.get("flashcards", []), start=1):
            body += f'''
<div class="flashcard">
<strong>Q:</strong> {card.get("question","")}
<button onclick="toggleFlashcard('flash{i}')">Show Answer</button>
<div id="flash{i}" style="display:none; margin-top:10px;">{card.get("answer","")}</div>
</div>
'''
        study_sections.append(("🗂", "Flashcards", body, False))

    study_icons_bg = ["#dbeafe", "#dcfce7", "#fef3c7", "#fee2e2", "#ede9fe", "#fce7f3"]
    study_html = ""
    for idx, (icon, title, body, open_default) in enumerate(study_sections):
        open_header = " open" if open_default else ""
        open_body = " open" if open_default else ""
        bg = study_icons_bg[idx % len(study_icons_bg)]
        study_html += f'''
<div class="study-section">
<div class="section-header{open_header}" onclick="toggleSection(this)">
<div class="section-icon" style="background:{bg};">{icon}</div>
<h2>{title}</h2><span class="toggle">▼</span>
</div>
<div class="section-body{open_body}">{body}</div>
</div>
'''

    # -----------------------------------------------------
    # FORMULAS PAGE — dedicated tab, formula grid only
    # -----------------------------------------------------
    formulas_page_html = ""
    if data.get("formulae"):
        formulas_page_html += '<div class="study-section"><div class="section-header open" onclick="toggleSection(this)">'
        formulas_page_html += '<div class="section-icon" style="background:#dbeafe;">📋</div><h2>All Formulae</h2><span class="toggle">▼</span></div>'
        formulas_page_html += '<div class="section-body open"><div class="formula-grid">'
        for f in data.get("formulae", []):
            formulas_page_html += f'''
<div class="formula-card">
<div class="f-label">{f.get("formula_name","")}</div>
<div class="f-eq">{f.get("formula","")}</div>
<div class="f-desc">{f.get("explanation","")}</div>
</div>
'''
        formulas_page_html += "</div></div></div>"
    else:
        formulas_page_html = '<p style="text-align:center;color:var(--muted);">No formulae for this topic.</p>'

    # -----------------------------------------------------
    # MCQ DATA — passed to JS as JSON, single quiz, no tiers
    # -----------------------------------------------------
    quiz_data = []
    for mcq in data.get("mcqs", []):
        options = [
            mcq.get("option_a", ""),
            mcq.get("option_b", ""),
            mcq.get("option_c", ""),
            mcq.get("option_d", ""),
        ]
        correct_letter = (mcq.get("correct_answer", "") or "A").strip().upper()
        correct_index = {"A": 0, "B": 1, "C": 2, "D": 3}.get(correct_letter, 0)
        quiz_data.append({
            "question": mcq.get("question", ""),
            "options": options,
            "correctIndex": correct_index,
            "explanation": mcq.get("explanation", ""),
        })
    quiz_json = json.dumps(quiz_data)
    quiz_count = len(quiz_data)

    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------
    footer_html = "<footer>"
    if logo_data_uri:
        footer_html += f'<div class="logo-block"><img src="{logo_data_uri}" alt="College Logo" class="college-logo"></div>'
    footer_html += '''
<p class="designed-by-label">Designed by</p>
<h3>Mrs Indhumathi T</h3>
<p>Research Scholar</p>
<p>Department of Mathematics</p>
<p>SCSVMV (Deemed to be University), Kanchipuram</p>
<br>
<p>&copy; 2026 All Rights Reserved</p>
</footer>
'''

    # -----------------------------------------------------
    # ASSEMBLE FULL PAGE
    # -----------------------------------------------------
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{topic or "Interactive Learning Material"}</title>
<style>
{css}
</style>
</head>
<body>

<nav>
  <div class="nav-logo">
    <div class="nav-logo-badge"><span>{badge_text}</span></div>
    <div class="nav-logo-text">
      <span class="nav-logo-main">{subject}</span>
    </div>
    {f'<img class="nav-college-logo" src="{logo_data_uri}" alt="College Logo">' if logo_data_uri else ''}
  </div>
  <div class="nav-links">
    <a class="active" onclick="showPage('study', this)">📖 Study</a>
    <a onclick="showPage('formulas', this)">📋 Formulas</a>
    <a onclick="showPage('mcq', this)">✏️ MCQ Test</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-content">
    <h1 class="hero-title">{topic}</h1>
    <div class="instructor-pill">
      <div class="inst-details">
        <span class="inst-label">Course Instructor</span>
        <span class="inst-name">{instructor}</span>
        <span class="inst-role">{department} &nbsp;·&nbsp; {programme}</span>
      </div>
    </div>
  </div>
</div>

<div id="page-study" class="page active">
<div class="container">
{study_html}
</div>
</div>

<div id="page-formulas" class="page">
<div class="container">
{formulas_page_html}
</div>
</div>

<div id="page-mcq" class="page">
<div class="container">

<div class="mcq-intro" id="mcq-intro">
<h2>✏️ MCQ Test</h2>
<p>{quiz_count} questions on {topic}. Test your understanding and see your score at the end.</p>
<button class="btn btn-primary" onclick="startQuiz()">🚀 Start Quiz</button>
</div>

<div class="quiz-container" id="quiz-container">
<div class="quiz-header">
<div class="qh-left">
<h3>{topic} Quiz</h3>
<p>Question <span id="qh-current">1</span> of <span id="qh-total">{quiz_count}</span></p>
</div>
<div class="progress-bar-wrap">
<div class="progress-bar-label"><span>Progress</span></div>
<div class="progress-bar-bg"><div class="progress-bar-fill" id="progress-fill" style="width:0%"></div></div>
</div>
</div>
<div id="quiz-question-area"></div>
</div>

<div class="results-panel" id="results-panel">
<div class="score-ring"><span id="score-pct">0%</span><span class="score-label">Score</span></div>
<h3 id="results-title">Great Job! 🎉</h3>
<p id="results-msg"></p>
<div class="result-stats">
<div class="result-stat rs-correct"><div class="rs-num" id="rs-correct">0</div><div class="rs-lbl">Correct</div></div>
<div class="result-stat rs-wrong"><div class="rs-num" id="rs-wrong">0</div><div class="rs-lbl">Wrong</div></div>
<div class="result-stat rs-score"><div class="rs-num" id="rs-score">0%</div><div class="rs-lbl">Score</div></div>
</div>
<button class="btn btn-secondary" onclick="retakeQuiz()">🔄 Retake Quiz</button>
<div id="review-area" style="text-align:left;margin-top:10px;"></div>
</div>

</div>
</div>

{footer_html}

<script>
window.__ILM_MCQS__ = {quiz_json};
{js}
</script>
</body>
</html>
"""
    return html
