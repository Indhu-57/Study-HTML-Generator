// ==========================================
// ILM Generator JavaScript
// ==========================================

// ----------------------------
// Charts (bar/line/pie/function graphs)
// ----------------------------
window.__ILM_CHART_INSTANCES__ = {};

(function renderRegisteredCharts() {
    var charts = window.__ILM_CHARTS__ || [];
    if (!charts.length) return;

    function init() {
        charts.forEach(function (entry) {
            var canvas = document.getElementById(entry.canvasId);
            if (!canvas || typeof Chart === 'undefined') return;
            try {
                var instance = new Chart(canvas.getContext('2d'), entry.config);
                window.__ILM_CHART_INSTANCES__[entry.canvasId] = instance;
            } catch (e) {
                console.error('Chart render failed for', entry.canvasId, e);
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

// ----------------------------
// Accordion sections
// ----------------------------
function toggleSection(headerEl) {
    headerEl.classList.toggle('open');
    var body = headerEl.nextElementSibling;
    body.classList.toggle('open');
}

function expandAllSections() {
    document.querySelectorAll('#page-study .section-header').forEach(function (h) {
        h.classList.add('open');
        h.nextElementSibling.classList.add('open');
    });
}

function collapseAllSections() {
    document.querySelectorAll('#page-study .section-header').forEach(function (h) {
        h.classList.remove('open');
        h.nextElementSibling.classList.remove('open');
    });
}

// ----------------------------
// Page navigation (Study / Formulas / MCQ Test)
// ----------------------------
function showPage(pageId, linkEl) {
    document.querySelectorAll('.page').forEach(function (p) {
        p.classList.remove('active');
    });
    var target = document.getElementById('page-' + pageId);
    target.classList.add('active');

    document.querySelectorAll('.nav-links a').forEach(function (a) {
        a.classList.remove('active');
    });
    if (linkEl) linkEl.classList.add('active');

    // Charts created while their tab was hidden render at zero size;
    // resize them now that the tab is actually visible.
    target.querySelectorAll('canvas').forEach(function (c) {
        var inst = window.__ILM_CHART_INSTANCES__[c.id];
        if (inst) inst.resize();
    });
}

// ----------------------------
// Flashcards
// ----------------------------
function toggleReveal(id) {
    var answer = document.getElementById(id);
    answer.style.display = (answer.style.display === 'none') ? 'block' : 'none';
}

// ----------------------------
// Quiz state
// ----------------------------
var QUIZ_DATA = window.__ILM_MCQS__ || [];
var currentIndex = 0;
var answers = [];

function startQuiz() {
    if (!QUIZ_DATA.length) return;
    currentIndex = 0;
    answers = [];
    document.getElementById('mcq-intro').style.display = 'none';
    document.getElementById('results-panel').classList.remove('active');
    document.getElementById('quiz-container').classList.add('active');
    renderQuestion();
}

function renderQuestion() {
    var q = QUIZ_DATA[currentIndex];
    var total = QUIZ_DATA.length;

    document.getElementById('qh-current').textContent = (currentIndex + 1);
    var pct = Math.round(((currentIndex) / total) * 100);
    document.getElementById('progress-fill').style.width = pct + '%';

    var html = '';
    html += '<div class="question-card">';
    html += '<div class="q-number">Question ' + (currentIndex + 1) + '</div>';
    html += '<div class="q-text">' + q.question + '</div>';
    html += '<div class="options" id="options-area">';
    q.options.forEach(function (opt, i) {
        var letter = String.fromCharCode(65 + i);
        html += '<div class="option" data-index="' + i + '" onclick="selectOption(' + i + ')">';
        html += '<div class="option-key">' + letter + '</div>';
        html += '<div class="option-text">' + opt + '</div>';
        html += '</div>';
    });
    html += '</div>';
    html += '<div class="explanation" id="explanation-box">' + (q.explanation || '') + '</div>';
    html += '<div class="quiz-nav">';
    html += '<button class="btn btn-primary" id="next-btn" style="display:none" onclick="nextQuestion()">' +
        (currentIndex === total - 1 ? 'See Results' : 'Next Question') + '</button>';
    html += '</div>';
    html += '</div>';

    document.getElementById('quiz-question-area').innerHTML = html;
}

function selectOption(index) {
    var q = QUIZ_DATA[currentIndex];
    var options = document.querySelectorAll('#options-area .option');
    options.forEach(function (el, i) {
        el.classList.remove('selected');
        if (i === q.correctIndex) el.classList.add('correct');
        if (i === index && i !== q.correctIndex) el.classList.add('wrong');
    });
    options[index].classList.add('selected');

    document.getElementById('explanation-box').classList.add('show');
    document.getElementById('next-btn').style.display = 'inline-block';

    options.forEach(function (el) {
        el.style.pointerEvents = 'none';
    });

    answers[currentIndex] = {
        qtext: q.question,
        selectedText: q.options[index],
        correctText: q.options[q.correctIndex],
        isCorrect: index === q.correctIndex,
        exp: q.explanation || ''
    };
}

function nextQuestion() {
    if (currentIndex < QUIZ_DATA.length - 1) {
        currentIndex++;
        renderQuestion();
    } else {
        showResults();
    }
}

function showResults() {
    document.getElementById('quiz-container').classList.remove('active');
    var panel = document.getElementById('results-panel');
    panel.classList.add('active');

    var total = QUIZ_DATA.length;
    var correct = answers.filter(function (a) { return a && a.isCorrect; }).length;
    var pct = total ? Math.round((correct / total) * 100) : 0;

    document.getElementById('score-pct').textContent = pct + '%';
    document.getElementById('rs-correct').textContent = correct;
    document.getElementById('rs-wrong').textContent = total - correct;
    document.getElementById('rs-score').textContent = pct + '%';
    document.getElementById('results-title').textContent = pct >= 60 ? 'Great Job! 🎉' : 'Keep Practicing! 💪';

    var msgs = ['Keep going!', 'Good attempt!', 'Well done!', 'Excellent!', 'Outstanding!'];
    var lvl = pct >= 90 ? 4 : pct >= 75 ? 3 : pct >= 60 ? 2 : pct >= 40 ? 1 : 0;
    document.getElementById('results-msg').textContent = msgs[lvl] + ' You scored ' + correct + ' out of ' + total + '.';

    var rv = '<h4 style="font-weight:700;color:var(--navy);margin-bottom:6px;">📋 Detailed Answer Review</h4>';
    rv += '<table class="review-table"><tr><th>#</th><th>Question &amp; Explanation</th><th>Your Answer</th><th>Correct Answer</th><th>Result</th></tr>';
    answers.forEach(function (a, i) {
        if (!a) return;
        rv += '<tr><td>' + (i + 1) + '</td><td>' + a.qtext + '<div class="rv-exp">💡 ' + a.exp + '</div></td><td>' + a.selectedText + '</td><td>' + a.correctText + '</td>';
        rv += '<td class="' + (a.isCorrect ? 'rv-correct' : 'rv-wrong') + '">' + (a.isCorrect ? '✓' : '✗') + '</td></tr>';
    });
    rv += '</table>';
    document.getElementById('review-area').innerHTML = rv;
}

function retakeQuiz() {
    document.getElementById('results-panel').classList.remove('active');
    document.getElementById('mcq-intro').style.display = 'block';
}

// ----------------------------
// Print
// ----------------------------
function printPage() {
    window.print();
}
