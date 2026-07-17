import json
import re
from datetime import datetime
from pathlib import Path

from venn import render_venn_svg
from charts import build_chart_config


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


def _render_practice_problems(practice_problems, diagram_fn):
    """
    Builds the "Practice Problems" study-section HTML. Shared between the
    quantitative layout (where it lives inside the Examples tab) and the
    theory layout (where it lives inside the Study tab, since there is no
    Examples tab for theory subjects).
    """
    if not practice_problems:
        return ""
    html = '<div class="study-section"><div class="section-header open" onclick="toggleSection(this)">'
    html += '<div class="section-icon" style="background:#dbeafe;">\U0001F9E0</div><h2>Practice Problems</h2><span class="toggle">\u25bc</span></div>'
    html += '<div class="section-body open">'
    for i, pp in enumerate(practice_problems, start=1):
        problem = _format_math(pp.get("problem", ""))
        answer = _format_math(pp.get("answer", ""))
        diagram_html = diagram_fn(pp.get("diagram"), f"pp{i}")
        html += f'''
<div class="practice-card">
<strong>Problem {i}:</strong> {problem}
{diagram_html}
<button onclick="toggleReveal('practice{i}')">Show Answer</button>
<div id="practice{i}" style="display:none; margin-top:10px;">{answer}</div>
</div>
'''
    html += "</div></div>"
    return html


def _slugify(text, fallback):
    slug = re.sub(r'[^a-z0-9]+', '-', (text or "").lower()).strip('-')
    return slug or fallback


def _render_flowchart_node(node):
    """Recursively renders one flowchart/mind-map node and its children
    as a nested <ul><li> tree (styled into a connected chart via CSS)."""
    if not isinstance(node, dict):
        return ""
    label = _format_math(node.get("label", ""))
    children = node.get("children") or []
    children_html = ""
    if children:
        children_html = "<ul>" + "".join(
            f"<li>{_render_flowchart_node(c)}</li>" for c in children if isinstance(c, dict)
        ) + "</ul>"
    return f'<span class="fc-label">{label}</span>{children_html}'


def _render_flowchart(spec):
    """Renders a {"type": "flowchart", "title": ..., "root": {...}} spec
    as a pure HTML/CSS tree diagram. Returns "" if the spec is invalid."""
    if not isinstance(spec, dict):
        return ""
    root = spec.get("root")
    if not isinstance(root, dict) or not root.get("label"):
        return ""
    title = spec.get("title", "")
    title_html = f'<div class="flowchart-title">{_format_math(title)}</div>' if title else ""
    tree_html = f'<ul class="flowchart-tree"><li>{_render_flowchart_node(root)}</li></ul>'
    return f'<div class="flowchart-wrap">{title_html}<div class="flowchart-scroll">{tree_html}</div></div>'


def _render_concept_groups(concept_groups):
    """
    Builds (nav_links_html, pages_html) for theory/practical-subject
    "concept groups" - one tab per group, each concept showing a
    quick_answer and a fully structured detailed_explanation (text, quote,
    and rule blocks). Each tab also gets a "jump to topic" dropdown so
    long tabs with many concepts are easy to navigate.
    Returns ([], []) if concept_groups is empty.
    """
    if not concept_groups:
        return [], []

    nav_links = []
    pages = []

    for gi, group in enumerate(concept_groups):
        title = group.get("group_title") or f"Topic {gi + 1}"
        tab_id = _slugify(title, f"concept{gi}")
        nav_links.append(f'    <a onclick="showPage(\'{tab_id}\', this)">{_format_math(title)}</a>')

        concept_blocks = []
        jump_options = []
        for ci, concept in enumerate(group.get("concepts", [])):
            c_title_raw = concept.get("title", "")
            c_title = _format_math(c_title_raw)
            c_anchor = _slugify(c_title_raw, f"{tab_id}-c{ci}")
            quick_answer = _format_math(concept.get("quick_answer", ""))
            jump_options.append((c_anchor, c_title_raw))

            diagram_html = _render_flowchart(concept.get("diagram"))

            detail_html = ""
            for block in concept.get("detailed_explanation", []):
                if not isinstance(block, dict):
                    continue
                block_type = (block.get("type") or "text").strip().lower()
                heading = block.get("heading")
                text = block.get("text", "")

                if block_type == "quote":
                    lines = [ln for ln in (text or "").split("\n") if ln.strip()]
                    quote_lines_html = "".join(f"<p>{_format_math(ln.strip())}</p>" for ln in lines)
                    heading_html = f'<div class="ae-quote-heading">{_format_math(heading)}</div>' if heading else ""
                    detail_html += f'<div class="ae-quote">{heading_html}<div class="ae-quote-lines">{quote_lines_html}</div></div>'
                elif block_type == "rule":
                    heading_html = f'<div class="ae-rule-heading">{_format_math(heading)}</div>' if heading else '<div class="ae-rule-heading">Rule</div>'
                    detail_html += f'<div class="ae-rule">{heading_html}<p class="ae-rule-text">{_format_math(text)}</p></div>'
                elif block_type == "example":
                    heading_html = f'<div class="ae-example-heading">{_format_math(heading)}</div>' if heading else '<div class="ae-example-heading">Example</div>'
                    detail_html += f'<div class="ae-example">{heading_html}<p class="ae-example-text">{_format_math(text)}</p></div>'
                else:
                    if heading:
                        detail_html += f'<p class="ae-subhead">{_format_math(heading)}</p>'
                    if text:
                        detail_html += f'<p class="ae-text">{_format_math(text)}</p>'

            concept_blocks.append(f'''
<div class="concept-block" id="{c_anchor}">
<div class="concept-title">{c_title}</div>
<div class="answer-box quick">
<div class="answer-label">Quick Answer</div>
<p>{quick_answer}</p>
</div>
<div class="answer-box detailed">
<div class="answer-label">Detailed Explanation</div>
{diagram_html}
{detail_html}
</div>
</div>''')

        jump_html = ""
        if len(jump_options) > 1:
            options_html = "".join(
                f'<option value="{anchor}">{_format_math(label)}</option>'
                for anchor, label in jump_options
            )
            jump_html = f'''
<div class="concept-jump">
<label for="jump-{tab_id}">Jump to topic:</label>
<select id="jump-{tab_id}" onchange="jumpToConcept(this)">
<option value="">Select a topic...</option>
{options_html}
</select>
</div>'''

        page_html = f'''
<div id="page-{tab_id}" class="page">
<div class="container">
<div class="concept-tab-intro">
<h2>{_format_math(title)}</h2>
<p>Clear, well-structured explanations for every concept in this topic \u2014 a quick answer for fast revision, and a fully developed explanation for deeper understanding.</p>
{jump_html}
</div>
{"".join(concept_blocks)}
</div>
</div>'''
        pages.append(page_html)

    return nav_links, pages


def generate_html(data):
    css = Path("assets/style.css").read_text(encoding="utf-8")
    js = Path("assets/script.js").read_text(encoding="utf-8")

    subject_type = (data.get("subject_type") or "").strip().lower()
    concept_groups = data.get("concept_groups") or []
    # Both "theory" and "practical" subjects use the concept-group tab
    # layout; only "quantitative" keeps the Definitions/Formulas/Examples
    # layout. Trust concept_groups actually being populated over the
    # subject_type label alone, in case Gemini sets the label
    # inconsistently with the content it actually produced.
    is_theory = bool(concept_groups) and subject_type != "quantitative"

    # Chart.js needs its configs registered as JS + a <canvas> placeholder;
    # collect them here as we walk the data, then inject once at the end.
    chart_registry = []

    def _diagram_html(spec, idx):
        """
        Dispatches a "diagram" spec to the right renderer:
        - venn2/venn3  -> inline static SVG (no JS needed)
        - bar/line/pie/function_graph -> a <canvas> placeholder + a
          registered Chart.js config, instantiated by script.js on load.
        Returns HTML (possibly empty string) - never raises.
        """
        if not isinstance(spec, dict):
            return ""
        kind = spec.get("type")

        if kind in ("venn2", "venn3"):
            svg = render_venn_svg(spec, idx=idx)
            return f'<div class="diagram-box">{svg}</div>' if svg else ""

        if kind in ("bar", "line", "pie", "function_graph"):
            config = build_chart_config(spec)
            if not config:
                return ""
            canvas_id = f"chart_{idx}"
            chart_registry.append({"canvasId": canvas_id, "config": config})
            return f'<div class="diagram-box"><canvas id="{canvas_id}"></canvas></div>'

        return ""

    metadata = data.get("metadata", {})
    topic = metadata.get("topic", "")
    instructor = metadata.get("course_instructor", "")
    department = metadata.get("department", "")
    programme = metadata.get("programme", "")
    subject = metadata.get("subject", "")
    generated_on = metadata.get("generated_on") or datetime.now().strftime("%d %B %Y")

    badge_text = _initials(subject)

    # -----------------------------------------------------
    # STUDY TAB - Introduction, Notes, Summary, Flashcards
    # (Practice Problems are appended here too for theory subjects,
    # since they have no Examples tab to live in.)
    # -----------------------------------------------------
    study_sections = []

    intro_body = ""
    if data.get("introduction"):
        intro_body += f'<p style="margin-bottom:16px;">{_format_math(data.get("introduction",""))}</p>'
    if data.get("learning_outcomes"):
        intro_body += '<p style="font-weight:700;color:var(--navy);margin-bottom:8px;">\U0001F3AF Learning Outcomes</p>'
        intro_body += '<ul class="key-points">'
        for item in data.get("learning_outcomes", []):
            intro_body += f"<li>{_format_math(item)}</li>"
        intro_body += "</ul>"
    if intro_body:
        study_sections.append(("\U0001F4D6", "Introduction & Learning Outcomes", intro_body, True))

    if data.get("important_notes"):
        body = '<ul class="key-points">'
        for note in data.get("important_notes", []):
            body += f"<li>{_format_math(note)}</li>"
        body += "</ul>"
        study_sections.append(("\U0001F4A1", "Important Notes", body, True))

    if data.get("summary"):
        summary_val = data.get("summary")
        body = '<ul class="summary-list">'
        if isinstance(summary_val, list):
            for point in summary_val:
                body += f"<li>{_format_math(point)}</li>"
        else:
            body += f"<li>{_format_math(summary_val)}</li>"
        body += "</ul>"
        study_sections.append(("\U0001F4C4", "Summary", body, False))

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
<h2>{sec_title}</h2><span class="toggle">\u25bc</span>
</div>
<div class="section-body{open_body}">{body}</div>
</div>
'''

    if is_theory:
        study_html += _render_practice_problems(data.get("practice_problems"), _diagram_html)

    # -----------------------------------------------------
    # CONCEPT GROUP TABS (theory subjects only)
    # -----------------------------------------------------
    concept_nav_links, concept_pages_html = _render_concept_groups(concept_groups) if is_theory else ([], [])

    # -----------------------------------------------------
    # DEFINITIONS TAB - term, meaning, and 3-10 examples each
    # (quantitative subjects only)
    # -----------------------------------------------------
    definitions_html = ""
    if not is_theory:
        if data.get("definitions"):
            for idx, d in enumerate(data.get("definitions", [])):
                examples = d.get("examples", [])
                examples_html = ""
                if examples:
                    examples_html = '<div class="def-examples"><strong>Examples:</strong><ul class="key-points">'
                    for ex in examples:
                        examples_html += f"<li>{_format_math(ex)}</li>"
                    examples_html += "</ul></div>"
                diagram_html = _diagram_html(d.get("diagram"), f"def{idx}")
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
    # WORKED EXAMPLES TAB (quantitative subjects only)
    # -----------------------------------------------------
    examples_page_html = ""
    if not is_theory:
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
                    heading += f" \u2014 {_format_math(problem)}"
                final_html = f'<div class="step-answer">Answer: {_format_math(final_answer)}</div>' if final_answer else ""
                diagram_html = _diagram_html(ex.get("diagram"), f"we{i}")
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

        examples_page_html += _render_practice_problems(data.get("practice_problems"), _diagram_html)

    # -----------------------------------------------------
    # FORMULAS PAGE - dedicated tab, formula grid only
    # (quantitative subjects only)
    # -----------------------------------------------------
    formulas_page_html = ""
    if not is_theory:
        if data.get("formulae"):
            formulas_page_html += '<div class="study-section"><div class="section-header open" onclick="toggleSection(this)">'
            formulas_page_html += '<div class="section-icon" style="background:#dbeafe;">\U0001F4CB</div><h2>All Formulae</h2><span class="toggle">\u25bc</span></div>'
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
    # MCQ DATA - passed to JS as JSON, single quiz, no tiers
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
    # NAV LINKS + PAGE SECTIONS
    # (differ depending on subject_type)
    # -----------------------------------------------------
    if is_theory:
        nav_extra = "\n".join(concept_nav_links)
        pages_extra = "\n".join(concept_pages_html)
    else:
        nav_extra = (
            '    <a onclick="showPage(\'definitions\', this)">\U0001F4DA Definitions</a>\n'
            '    <a onclick="showPage(\'formulas\', this)">\u2797 Formulas</a>\n'
            '    <a onclick="showPage(\'examples\', this)">\u270F\uFE0F Examples</a>'
        )
        pages_extra = f'''
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
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
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
    <a class="active" onclick="showPage('study', this)">\U0001F4D6 Study</a>
{nav_extra}
    <a onclick="showPage('mcq', this)">\u2705 MCQ Test</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-content">
    <h1 class="hero-title">{topic}</h1>
    <div class="instructor-pill">
      <div class="inst-details">
        <span class="inst-label">Course Instructor</span>
        <span class="inst-name">{instructor}</span>
        <span class="inst-role">{department} &nbsp;\u00b7&nbsp; {programme}</span>
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
<button class="btn btn-secondary btn-sm" onclick="printPage()">\U0001F5A8 Print</button>
</div>
</div>
{study_html}
</div>
</div>

{pages_extra}

<div id="page-mcq" class="page">
<div class="container">

<div class="mcq-intro" id="mcq-intro">
<h2>\u270F\uFE0F MCQ Test</h2>
<p>Test your understanding of {topic} and see your score at the end.</p>
<button class="btn btn-primary" onclick="startQuiz()">\U0001F680 Start Quiz</button>
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
<h3 id="results-title">Great Job! \U0001F389</h3>
<p id="results-msg"></p>
<div class="result-stats">
<div class="result-stat rs-correct"><div class="rs-num" id="rs-correct">0</div><div class="rs-lbl">Correct</div></div>
<div class="result-stat rs-wrong"><div class="rs-num" id="rs-wrong">0</div><div class="rs-lbl">Wrong</div></div>
<div class="result-stat rs-score"><div class="rs-num" id="rs-score">0%</div><div class="rs-lbl">Score</div></div>
</div>
<button class="btn btn-secondary" onclick="retakeQuiz()">\U0001F504 Retake Quiz</button>
<div id="review-area" style="text-align:left;margin-top:10px;"></div>
</div>

</div>
</div>

{footer_html}

<script>
window.__ILM_MCQS__ = {quiz_json};
window.__ILM_CHARTS__ = {json.dumps(chart_registry)};
{js}
</script>
</body>
</html>
"""
    return html
