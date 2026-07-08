import json
import re
from datetime import datetime
from pathlib import Path

from venn import render_venn_svg


_EXPONENT_RE = re.compile(r'\^(\([^)]*\)|-?[A-Za-z0-9]+)')
_LEADING_STEP_NUM_RE = re.compile(r'^\s*(?:step\s*)?\d+\s*[\.\):]\s*', re.IGNORECASE)


def _format_math(text):
    """
    Turns caret-style exponents like (a + b)^2 or x^3589 into proper
    HTML superscripts: (a + b)<sup>2</sup>, x<sup>3589</sup>.
    Leaves everything else untouched.
    """
    if not isinstance(text, str) or "^" not in text:
        return text

    def repl(m):
        exp = m.group(1)
        if exp.startswith("(") and exp.endswith(")"):
            exp = exp[1:-1]
        return f"<sup>{exp}</sup>"

    return _EXPONENT_RE.sub(repl, text)


def _clean_step(text):
    """
    Strips a redundant leading '1.' / 'Step 1:' style prefix from a step
    string (since steps are already rendered with their own numbering),
    then applies math formatting.
    """
    if not isinstance(text, str):
        return text
    text = _LEADING_STEP_NUM_RE.sub("", text).strip()
    return _format_math(text)


def _normalize_worked_example(ex):
    """
    Different Gemini runs have returned worked examples shaped differently:
    - {title, problem, steps: [...], solution: "final answer"}
    - {problem, solution: [...steps...]}  (steps nested inside 'solution')
    This normalizes any of those into (title, problem, steps, final_answer).
    """
    title = ex.get("title") or ex.get("example_title") or ""
    problem = ex.get("problem") or ex.get("question") or ""

    steps = ex.get("steps")
    solution = ex.get("solution")

    if isinstance(steps, list) and steps:
        final_answer = ex.get("answer") or (solution if isinstance(solution, str) else "")
    elif isinstance(solution, list):
        steps = solution
        final_answer = ex.get("answer") or (steps[-1] if steps else "")
    else:
        steps = steps if isinstance(steps, list) else []
        final_answer = solution if isinstance(solution, str) else (ex.get("answer") or "")

    return title, problem, steps, final_answer


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

    badge_text = _initials(subject)

    # -----------------------------------------------------
    # STUDY TAB — Introduction, Notes, Summary, Flashcards only
    # (Definitions, Formulae, and Worked Examples now have their own tabs)
    # -----------------------------------------------------
    study_sections = []

    intro_body = ""
    if data.get("introduction"):
        intro_body += f'<p style="margin-bottom:16px;">{_format_math(data.get("introduction",""))}</p>'
    if data.get("learning_outcomes"):
        intro_body += '<p style="font-weight:700;color:var(--navy);margin-bottom:8px;">🎯 Learning Outcomes</p>'
        intro_body += '<ul class="key-points">'
        for item in data.get("learning_outcomes", []):
            intro_body += f"<li>{_format_math(item)}</li>"
        intro_body += "</ul>"
    if intro_body:
        study_sections.append(("📖", "Introduction & Learning Outcomes", intro_body, True))

    if data.get("important_notes"):
        body = '<ul class="key-points">'
        for note in data.get("important_notes", []):
            body += f"<li>{_format_math(note)}</li>"
        body += "</ul>"
        study_sections.append(("💡", "Important Notes", body, True))

    if data.get("summary"):
        summary_val = data.get("summary")
        body = '<ul class="summary-list">'
        if isinstance(summary_val, list):
            for point in summary_val:
                body += f"<li>{_format_math(point)}</li>"
        else:
            body += f"<li>{_format_math(summary_val)}</li>"
        body += "</ul>"
        study_sections.append(("📄", "Summary", body, False))

    study_icons_bg = ["#dbeafe", "#dcfce7", "#fef3c7", "#fee2e2", "#ede9fe", "#fce7f3"]
    study_html = ""
    for idx, (icon, sec_title, body, open_default) in enumerate(study_sections):
        open_header = " open" if open_default else ""
        open_body = " open" if open_default else ""
        bg = study_icons_bg[idx % len(study_icons_bg)]
        study_html += f'''
<div class="study-section">
<div class="section-header{open_header}" onclick="toggleSection(this)">
<div class="section-icon" style="background:{bg};">{icon}</div>
<h2>{sec_title}</h2><span class="toggle">▼</span>
</div>
<div class="section-body{open_body}">{body}</div>
</div>
'''

    # -----------------------------------------------------
    # DEFINITIONS TAB — term, meaning, and 3-10 examples each
    # -----------------------------------------------------
    definitions_html = ""
    if data.get("definitions"):
        for idx, d in enumerate(data.get("definitions", [])):
            examples = d.get("examples", [])
            examples_html = ""
            if examples:
                examples_html = '<div class="def-examples"><strong>Examples:</strong><ul class="key-points">'
                for ex in examples:
                    examples_html += f"<li>{_format_math(ex)}</li>"
                examples_html += "</ul></div>"
            diagram_svg = render_venn_svg(d.get("diagram"), idx=f"def{idx}")
            diagram_html = f'<div class="diagram-box">{diagram_svg}</div>' if diagram_svg else ""
            definitions_html += f'''
<div class="def-box">
<div class="def-title">{d.get("term","")}</div>
<p>{_format_math(d.get("meaning",""))}</p>
{diagram_html}
{examples_html}
</div>
'''
    else:
        definitions_html = '<p style="text-align:center;color:var(--muted);">No definitions for this topic.</p>'

    # -----------------------------------------------------
    # WORKED EXAMPLES TAB
    # -----------------------------------------------------
    examples_page_html = ""
    if data.get("worked_examples"):
        for i, ex in enumerate(data.get("worked_examples", []), start=1):
            title, problem, steps, final_answer = _normalize_worked_example(ex)
            steps_html = ""
            for step in steps:
                cleaned = _clean_step(step)
                if cleaned:
                    steps_html += f'<p class="step-line">{cleaned}</p>'
            heading = _format_math(title) if title else "Worked Example"
            if problem:
                heading += f" — {_format_math(problem)}"
            final_html = f'<div class="step-answer">Answer: {_format_math(final_answer)}</div>' if final_answer else ""
            diagram_svg = render_venn_svg(ex.get("diagram"), idx=f"we{i}")
            diagram_html = f'<div class="diagram-box">{diagram_svg}</div>' if diagram_svg else ""
            examples_page_html += f'''
<div class="worked-example">
<div class="we-q">{heading}</div>
{diagram_html}
<div class="step-list">{steps_html}</div>
{final_html}
</div>
'''
    else:
        examples_page_html = '<p style="text-align:center;color:var(--muted);">No worked examples for this topic.</p>'

    if data.get("practice_problems"):
        examples_page_html += '<div class="study-section"><div class="section-header open" onclick="toggleSection(this)">'
        examples_page_html += '<div class="section-icon" style="background:#dbeafe;">🧠</div><h2>Practice Problems</h2><span class="toggle">▼</span></div>'
        examples_page_html += '<div class="section-body open">'
        for i, pp in enumerate(data.get("practice_problems", []), start=1):
            problem = _format_math(pp.get("problem", ""))
            answer = _format_math(pp.get("answer", ""))
            diagram_svg = render_venn_svg(pp.get("diagram"), idx=f"pp{i}")
            diagram_html = f'<div class="diagram-box">{diagram_svg}</div>' if diagram_svg else ""
            examples_page_html += f'''
<div class="practice-card">
<strong>Problem {i}:</strong> {problem}
{diagram_html}
<button onclick="toggleReveal('practice{i}')">Show Answer</button>
<div id="practice{i}" style="display:none; margin-top:10px;">{answer}</div>
</div>
'''
        examples_page_html += "</div></div>"

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
<div class="f-label">{_format_math(f.get("formula_name",""))}</div>
<div class="f-eq">{_format_math(f.get("formula",""))}</div>
<div class="f-desc">{_format_math(f.get("explanation",""))}</div>
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
            _format_math(mcq.get("option_a", "")),
            _format_math(mcq.get("option_b", "")),
            _format_math(mcq.get("option_c", "")),
            _format_math(mcq.get("option_d", "")),
        ]
        correct_letter = (mcq.get("correct_answer", "") or "A").strip().upper()
        correct_index = {"A": 0, "B": 1, "C": 2, "D": 3}.get(correct_letter, 0)
        quiz_data.append({
            "question": _format_math(mcq.get("question", "")),
            "options": options,
            "correctIndex": correct_index,
            "explanation": _format_math(mcq.get("explanation", "")),
        })
    quiz_json = json.dumps(quiz_data)
    quiz_count = len(quiz_data)

    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------
    footer_html = "<footer>"
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
  </div>
  <div class="nav-links">
    <a class="active" onclick="showPage('study', this)">📖 Study</a>
    <a onclick="showPage('definitions', this)">📚 Definitions</a>
    <a onclick="showPage('formulas', this)">➗ Formulas</a>
    <a onclick="showPage('examples', this)">✏️ Examples</a>
    <a onclick="showPage('mcq', this)">✅ MCQ Test</a>
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
<div class="section-controls">
<span class="generated-date">Generated on {generated_on}</span>
<div>
<button class="btn btn-secondary btn-sm" onclick="expandAllSections()">Expand All</button>
<button class="btn btn-secondary btn-sm" onclick="collapseAllSections()">Collapse All</button>
<button class="btn btn-secondary btn-sm" onclick="printPage()">🖨 Print</button>
</div>
</div>
{study_html}
</div>
</div>

<div id="page-definitions" class="page">
<div class="container">
{definitions_html}
</div>
</div>

<div id="page-formulas" class="page">
<div class="container">
{formulas_page_html}
</div>
</div>

<div id="page-examples" class="page">
<div class="container">
{examples_page_html}
</div>
</div>

<div id="page-mcq" class="page">
<div class="container">

<div class="mcq-intro" id="mcq-intro">
<h2>✏️ MCQ Test</h2>
<p>Test your understanding of {topic} and see your score at the end.</p>
<button class="btn btn-primary" onclick="startQuiz()">🚀 Start Quiz</button>
</div>

<div class="quiz-container" id="quiz-container">
<div class="quiz-header">
<div class="qh-left">
<h3>{topic} Quiz</h3>
<p>Question <span id="qh-current">1</span></p>
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
