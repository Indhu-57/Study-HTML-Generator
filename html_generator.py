/* ==========================================
   ILM Generator - matches reference template style
   ========================================== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Merriweather:wght@400;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root{
  --navy:#0f2447;--blue:#1a4080;--sky:#2563eb;--accent:#f59e0b;
  --accent2:#10b981;--red:#ef4444;--white:#fff;
  --gray:#64748b;--border:#dde3f0;--card:#fff;--text:#1e293b;--muted:#475569;
  --pale-green:#bfe6c8;--pale-green-dark:#9ed4ac;--pale-blue:#bcd9f2;--pale-blue-dark:#9cc3ea;
}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Inter',sans-serif;background:#eef2fb;color:var(--text);line-height:1.7;}

/* NAV */
nav{background:linear-gradient(135deg,var(--pale-green) 0%,var(--pale-green-dark) 100%);padding:8px 20px;display:flex;align-items:center;gap:10px;position:sticky;top:0;z-index:100;box-shadow:0 2px 16px rgba(0,0,0,.15);flex-wrap:nowrap;}
.nav-logo{display:flex;align-items:center;gap:8px;flex-shrink:0;}
.nav-logo-badge{display:flex;align-items:center;justify-content:center;width:38px;height:38px;border-radius:9px;flex-shrink:0;position:relative;background:var(--navy);border:1.5px solid var(--accent);box-shadow:inset 0 0 0 1px rgba(245,158,11,.3),0 0 8px rgba(245,158,11,.18);}
.nav-logo-badge span{font-family:'Merriweather',serif;font-weight:800;font-size:.8rem;letter-spacing:.3px;color:var(--accent);}
.nav-logo-text{display:flex;flex-direction:column;line-height:1.1;}
.nav-logo-main{color:var(--navy);font-weight:800;font-size:.92rem;font-family:'Merriweather',serif;letter-spacing:.2px;white-space:nowrap;}
.nav-college-logo{height:30px;object-fit:contain;flex-shrink:0;margin-left:4px;padding-left:10px;border-left:1px solid rgba(15,36,71,.25);}
.nav-links{display:flex;gap:3px;flex-wrap:nowrap;margin-left:auto;overflow-x:auto;}
.nav-links a{color:var(--navy);text-decoration:none;font-size:.72rem;font-weight:600;padding:5px 10px;border-radius:18px;transition:all .2s;white-space:nowrap;cursor:pointer;}
.nav-links a:hover,.nav-links a.active{background:var(--navy);color:#fff;}

/* HERO */
.hero{background:linear-gradient(135deg,var(--pale-blue) 0%,#a8c9ec 55%,var(--pale-blue-dark) 100%);color:#16335c;min-height:76px;position:relative;overflow:hidden;display:flex;align-items:center;padding:10px 0;}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 25% 50%,rgba(255,255,255,.25) 0%,transparent 65%),radial-gradient(ellipse at 75% 40%,rgba(245,158,11,.12) 0%,transparent 60%);}
.hero-content{position:relative;z-index:1;max-width:1100px;width:100%;margin:0 auto;padding:0 32px;display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap;}
.hero-title{font-family:'Merriweather',serif;font-size:1.25rem;font-weight:700;line-height:1.1;}

/* INSTRUCTOR PILL */
.instructor-pill{display:inline-flex;align-items:center;gap:9px;background:rgba(255,255,255,.4);border:1px solid rgba(22,51,92,.18);border-radius:50px;padding:6px 14px;flex-shrink:0;}
.inst-details{display:flex;flex-direction:column;}
.inst-label{font-size:.56rem;color:#8a5200;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:0;line-height:1.1;}
.inst-name{font-size:.78rem;font-weight:700;color:#16335c;line-height:1.15;}
.inst-role{font-size:.6rem;color:#3d5a82;line-height:1.2;}

/* SECTION CONTROLS */
.section-controls{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:18px;}
.generated-date{font-size:.8rem;color:var(--muted);}
.btn-sm{padding:6px 14px;font-size:.76rem;}

/* LAYOUT */
.container{max-width:960px;margin:0 auto;padding:40px 20px;}
.page{display:none;}.page.active{display:block;}

/* STUDY SECTIONS */
.study-section{background:var(--card);border-radius:16px;border:1px solid var(--border);margin-bottom:24px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.05);}
.section-header{padding:18px 26px;display:flex;align-items:center;gap:14px;cursor:pointer;user-select:none;background:linear-gradient(90deg,#f8faff,white);border-bottom:1px solid var(--border);}
.section-header:hover{background:#f0f4ff;}
.section-icon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;background:#dbeafe;}
.section-header h2{font-size:1rem;font-weight:700;color:var(--navy);flex:1;}
.section-header .toggle{color:var(--gray);font-size:1.1rem;transition:transform .3s;}
.section-header.open .toggle{transform:rotate(180deg);}
.section-body{padding:26px;display:none;}.section-body.open{display:block;}

/* DEF BOXES */
.def-box{border-left:4px solid var(--sky);background:linear-gradient(90deg,#f0f6ff,#f8fbff);border-radius:0 10px 10px 0;padding:14px 18px;margin-bottom:14px;}
.def-box .def-title{font-weight:700;color:var(--navy);font-size:.97rem;margin-bottom:5px;display:flex;align-items:center;gap:8px;}
.def-box .def-title span{background:var(--sky);color:white;font-size:.62rem;padding:2px 8px;border-radius:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;}
.def-box p{color:var(--text);font-size:.93rem;}
.diagram-box{background:#fbfdff;border:1px solid var(--border);border-radius:10px;padding:14px;margin:12px 0;display:flex;justify-content:center;}
.diagram-box svg{max-width:280px;}
.def-examples{margin-top:10px;padding-top:10px;border-top:1px dashed rgba(37,99,235,.25);}
.def-examples strong{color:var(--navy);font-size:.85rem;}
.def-examples ul{margin-top:6px;}

/* FORMULAS */
.formula-grid{display:flex;flex-direction:column;gap:14px;margin:14px 0;}
.formula-card{background:#fff;border:1px solid var(--border);border-radius:12px;overflow:hidden;}
.formula-card .f-label{background:#eff6ff;color:#1d4ed8;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.6px;padding:10px 16px;border-bottom:1px solid #dbeafe;}
.formula-card .f-eq{font-family:'JetBrains Mono',monospace;font-size:1rem;color:#c2410c;font-weight:600;line-height:1.7;padding:14px 16px 4px;}
.formula-card .f-desc{font-size:.85rem;color:var(--text);padding:4px 16px 14px;line-height:1.6;}

/* WORKED EXAMPLE */
.worked-example{background:#f0fdf8;border:1px solid #bbf7d0;border-radius:12px;padding:16px 18px;margin:12px 0;}
.worked-example .we-q{font-weight:700;color:var(--navy);margin-bottom:12px;font-size:.95rem;}
.step-list{display:flex;flex-direction:column;gap:2px;}
.step-line{color:#065f46;font-size:.89rem;line-height:1.75;padding:6px 0;border-bottom:1px dashed rgba(6,95,70,.15);}
.step-line:last-child{border-bottom:none;}
.step-text{color:#065f46;font-size:.89rem;line-height:1.6;padding-top:1px;}
.step-answer{margin-top:14px;padding:10px 14px;background:#065f46;color:white;border-radius:8px;font-size:.87rem;font-weight:600;}
.worked-example sup{font-size:.7em;}

/* PRACTICE PROBLEMS */
.practice-card{background:#eff6ff;border:1px solid #bfdbfe;border-left:5px solid var(--sky);padding:15px 18px;margin-bottom:14px;border-radius:0 10px 10px 0;}
.practice-card button{margin-top:8px;}

/* NOTE BOX */
.note-box{background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:13px 16px;margin:12px 0;font-size:.86rem;color:#78350f;}
.note-box strong{color:#92400e;}

/* KEY POINTS */
.key-points{list-style:none;}
.key-points li{padding:7px 0;border-bottom:1px solid #f1f5f9;padding-left:22px;position:relative;font-size:.91rem;}
.key-points li::before{content:'\25b6';position:absolute;left:0;color:var(--sky);font-size:.6rem;top:11px;}
.key-points li:last-child{border-bottom:none;}

/* SUMMARY */
.summary-list{list-style:none;}
.summary-list li{padding:8px 0;border-bottom:1px solid #f1f5f9;padding-left:22px;position:relative;font-size:.91rem;}
.summary-list li::before{content:'\2713';position:absolute;left:0;color:var(--accent2);font-weight:700;top:8px;}
.summary-list li:last-child{border-bottom:none;}

/* FLASHCARDS */
.flashcard{background:#fff8e1;border:1px solid #fde68a;border-left:5px solid var(--accent);padding:15px 18px;margin-bottom:14px;border-radius:0 10px 10px 0;}
.flashcard button{margin-top:8px;}

/* CONCEPT TABS (theory-subject quick answer / detailed explanation) */
.concept-tab-intro{background:var(--card);border-radius:16px;border:1px solid var(--border);padding:24px 28px;margin-bottom:22px;box-shadow:0 2px 10px rgba(0,0,0,.05);}
.concept-tab-intro h2{font-family:'Merriweather',serif;font-size:1.3rem;color:var(--navy);margin-bottom:6px;}
.concept-tab-intro p{color:var(--muted);font-size:.88rem;}
.concept-block{background:var(--card);border-radius:16px;border:1px solid var(--border);margin-bottom:22px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.05);}
.concept-block .concept-title{background:linear-gradient(90deg,var(--navy),var(--blue));color:#fff;font-family:'Merriweather',serif;font-weight:700;font-size:1.02rem;padding:16px 22px;}
.answer-box{padding:16px 22px;}
.answer-box .answer-label{display:inline-block;font-size:.66rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;padding:3px 11px;border-radius:10px;margin-bottom:10px;}
.answer-box.quick{background:#f0f6ff;border-bottom:1px solid var(--border);}
.answer-box.quick .answer-label{background:var(--sky);color:#fff;}
.answer-box.quick p{font-size:.92rem;color:var(--text);line-height:1.65;}
.answer-box.detailed{background:#fdfefe;}
.answer-box.detailed .answer-label{background:var(--accent2);color:#fff;}
.answer-box.detailed .ae-subhead{font-weight:700;color:var(--navy);font-size:.9rem;margin:12px 0 4px;}
.answer-box.detailed .ae-subhead:first-of-type{margin-top:2px;}
.answer-box.detailed .ae-text{font-size:.9rem;color:var(--text);line-height:1.7;margin-bottom:2px;}
/* Poetic / verse quotation blocks: kept visually separate from the
   surrounding explanation, with each original line on its own row. */
.answer-box.detailed .ae-quote{background:#f8f5ee;border-left:4px solid var(--accent);border-radius:0 8px 8px 0;padding:12px 18px;margin:12px 0;}
.answer-box.detailed .ae-quote-heading{font-weight:700;color:#92400e;font-size:.78rem;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;}
.answer-box.detailed .ae-quote-lines p{font-family:'Merriweather',serif;font-style:italic;color:#4b3f2a;font-size:.92rem;line-height:1.85;margin:0;}
/* Grammar / must-memorise rule blocks: distinct highlight so the exact
   rule stands out from the surrounding explanation. */
.answer-box.detailed .ae-rule{background:#fef2f2;border:1px solid #fecaca;border-left:4px solid var(--red);border-radius:0 8px 8px 0;padding:12px 18px;margin:12px 0;}
.answer-box.detailed .ae-rule-heading{font-weight:700;color:#b91c1c;font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;}
.answer-box.detailed .ae-rule-text{color:#7f1d1d;font-size:.92rem;font-weight:600;line-height:1.6;margin:0;}
/* Illustrative examples embedded in an explanation: pulled out into
   their own callout, separate from the surrounding paragraph. */
.answer-box.detailed .ae-example{background:#f0fdf4;border:1px solid #bbf7d0;border-left:4px solid var(--accent2);border-radius:0 8px 8px 0;padding:12px 18px;margin:12px 0;}
.answer-box.detailed .ae-example-heading{font-weight:700;color:#047857;font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;}
.answer-box.detailed .ae-example-text{color:#065f46;font-size:.9rem;line-height:1.65;margin:0;}

/* Jump-to-topic dropdown at the top of each concept-group tab */
.concept-jump{margin-top:16px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
.concept-jump label{font-size:.8rem;font-weight:600;color:var(--muted);}
.concept-jump select{padding:7px 12px;border-radius:8px;border:1.5px solid var(--border);font-size:.85rem;color:var(--navy);background:#fff;cursor:pointer;font-family:'Inter',sans-serif;}
.concept-jump select:focus{outline:none;border-color:var(--sky);}

/* Flowchart / mind-map tree diagram (pure HTML+CSS, no JS needed) */
.flowchart-wrap{background:#fbfdff;border:1px solid var(--border);border-radius:10px;padding:20px 16px;margin:14px 0;}
.flowchart-title{font-weight:700;color:var(--navy);font-size:.9rem;margin-bottom:14px;text-align:center;}
.flowchart-scroll{overflow-x:auto;padding-bottom:6px;}
.flowchart-tree,.flowchart-tree ul{list-style:none;margin:0;padding:0;}
.flowchart-tree{display:flex;justify-content:center;}
.flowchart-tree ul{display:flex;padding-top:20px;position:relative;}
.flowchart-tree li{position:relative;padding:0 12px;text-align:center;list-style:none;}
.flowchart-tree ul li{padding-top:20px;}
.flowchart-tree ul li::before{content:'';position:absolute;top:0;left:50%;border-left:2px solid var(--border);height:20px;}
.flowchart-tree ul::before{content:'';position:absolute;top:0;left:0;right:0;border-top:2px solid var(--border);}
.flowchart-tree ul li:first-child::after,.flowchart-tree ul li:last-child::after{content:'';position:absolute;top:0;height:2px;background:#fbfdff;width:50%;}
.flowchart-tree ul li:first-child::after{left:0;}
.flowchart-tree ul li:last-child::after{right:0;}
.flowchart-tree ul:has(> li:only-child)::before{display:none;}
.flowchart-tree ul li:only-child::before{display:none;}
.flowchart-tree .fc-label{display:inline-block;border:1.5px solid var(--sky);border-radius:8px;padding:7px 14px;background:#fff;font-size:.8rem;font-weight:600;color:var(--navy);white-space:nowrap;}
.flowchart-tree > li > .fc-label{border-color:var(--navy);background:var(--navy);color:#fff;}

/* Block diagram (system/architecture "boxes and arrows" figures, e.g.
   a CPU organisation diagram with a grouped container) */
.bd-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:nowrap;}
.bd-col{display:flex;flex-direction:column;gap:10px;align-items:center;}
.bd-chain{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap;}
.bd-box{background:#f1f5f9;border:1.5px solid #94a3b8;border-radius:8px;padding:10px 16px;text-align:center;min-width:110px;}
.bd-box .bd-label{font-size:.82rem;font-weight:700;color:var(--navy);}
.bd-box .bd-sublabel{font-size:.72rem;color:var(--muted);margin-top:4px;}
.bd-box-internal{background:#d9f2df;border-color:#9ed4ac;width:100%;min-width:150px;}
.bd-arrow{font-size:1.3rem;color:var(--navy);flex-shrink:0;padding:0 2px;}
.bd-group{border:2px solid var(--navy);border-radius:10px;padding:16px 18px 12px;background:#fff;display:flex;flex-direction:column;align-items:center;}
.bd-group-label{font-weight:800;color:#7f1d1d;font-size:.88rem;text-align:center;margin-bottom:10px;}
.bd-group-inner{display:flex;flex-direction:column;align-items:center;width:100%;}
.bd-vconn-wrap{display:flex;gap:14px;font-size:1.15rem;color:var(--navy);padding:2px 0;}
.bd-vconn-up,.bd-vconn-down{line-height:1;}
@media(max-width:640px){
.bd-row{flex-direction:column;}
.bd-arrow{transform:rotate(90deg);}
}

/* MCQ INTRO */
.mcq-intro{background:var(--card);border-radius:16px;border:1px solid var(--border);padding:40px;text-align:center;margin-bottom:24px;box-shadow:0 2px 10px rgba(0,0,0,.05);}
.mcq-intro h2{font-family:'Merriweather',serif;font-size:1.8rem;color:var(--navy);margin-bottom:10px;}
.mcq-intro p{color:var(--muted);margin-bottom:28px;font-size:.93rem;}

/* QUIZ */
.quiz-container{display:none;}.quiz-container.active{display:block;}
.quiz-header{background:var(--navy);color:white;border-radius:14px;padding:20px 26px;display:flex;align-items:center;justify-content:space-between;margin-bottom:22px;flex-wrap:wrap;gap:14px;}
.quiz-header .qh-left h3{font-size:1.05rem;font-weight:700;margin-bottom:3px;}
.quiz-header .qh-left p{font-size:.8rem;color:#94a3b8;}
.progress-bar-wrap{flex:1;min-width:150px;max-width:260px;}
.progress-bar-label{font-size:.76rem;color:#94a3b8;margin-bottom:5px;display:flex;justify-content:space-between;}
.progress-bar-bg{background:rgba(255,255,255,.15);border-radius:10px;height:7px;}
.progress-bar-fill{background:var(--accent);border-radius:10px;height:7px;transition:width .4s;}
.question-card{background:var(--card);border-radius:14px;border:1px solid var(--border);padding:26px;margin-bottom:18px;box-shadow:0 2px 8px rgba(0,0,0,.04);}
.q-number{display:inline-block;background:var(--sky);color:white;font-size:.7rem;font-weight:700;padding:3px 10px;border-radius:10px;letter-spacing:1px;text-transform:uppercase;margin-bottom:13px;}
.q-text{font-size:.98rem;font-weight:600;color:var(--navy);margin-bottom:18px;line-height:1.6;}
.options{display:grid;gap:9px;}
.option{display:flex;align-items:center;gap:13px;padding:12px 16px;border:2px solid var(--border);border-radius:10px;cursor:pointer;transition:all .2s;background:white;}
.option:hover{border-color:var(--sky);background:#f0f6ff;}
.option.selected{border-color:var(--sky);background:#eff6ff;}
.option.correct{border-color:var(--accent2);background:#f0fdf4;}
.option.wrong{border-color:var(--red);background:#fff5f5;}
.option-key{width:29px;height:29px;border-radius:50%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.8rem;color:var(--muted);flex-shrink:0;transition:all .2s;}
.option.selected .option-key{background:var(--sky);color:white;}
.option.correct .option-key{background:var(--accent2);color:white;}
.option.wrong .option-key{background:var(--red);color:white;}
.option-text{font-size:.9rem;color:var(--text);}
.explanation{display:none;margin-top:14px;padding:12px 16px;background:#fffbeb;border:1px solid #fde68a;border-radius:10px;font-size:.86rem;color:#78350f;line-height:1.6;}
.explanation.show{display:block;}
.quiz-nav{display:flex;gap:12px;justify-content:flex-end;margin-top:8px;}
.btn{padding:10px 22px;border-radius:10px;font-weight:600;font-size:.86rem;cursor:pointer;border:none;transition:all .2s;}
.btn-primary{background:var(--sky);color:white;}.btn-primary:hover{background:#1d4ed8;}
.btn-secondary{background:white;color:var(--navy);border:2px solid var(--border);}.btn-secondary:hover{border-color:var(--sky);color:var(--sky);}
.btn-success{background:var(--accent2);color:white;}.btn-success:hover{background:#059669;}

/* RESULTS */
.results-panel{background:var(--card);border-radius:16px;border:1px solid var(--border);padding:40px;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,.05);display:none;}
.results-panel.active{display:block;}
.score-ring{width:120px;height:120px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;margin:0 auto 22px;font-size:2.2rem;font-weight:800;color:white;border:5px solid rgba(255,255,255,.3);background:var(--sky);}
.score-ring .score-label{font-size:.68rem;font-weight:500;opacity:.85;letter-spacing:1px;text-transform:uppercase;margin-top:2px;}
.results-panel h3{font-family:'Merriweather',serif;font-size:1.5rem;color:var(--navy);margin-bottom:8px;}
.results-panel p{color:var(--muted);margin-bottom:22px;}
.result-stats{display:flex;justify-content:center;gap:28px;flex-wrap:wrap;margin-bottom:24px;}
.result-stat{text-align:center;}
.result-stat .rs-num{font-size:1.7rem;font-weight:800;}
.result-stat .rs-lbl{font-size:.73rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;}
.rs-correct .rs-num{color:var(--accent2);}.rs-wrong .rs-num{color:var(--red);}.rs-score .rs-num{color:var(--sky);}
.review-table{width:100%;border-collapse:collapse;margin-top:22px;border-radius:10px;overflow:hidden;}
.review-table th{background:var(--navy);color:white;padding:9px 12px;font-size:.8rem;text-align:left;}
.review-table td{padding:9px 12px;font-size:.83rem;border-bottom:1px solid var(--border);vertical-align:top;}
.review-table tr:nth-child(even) td{background:#f8faff;}
.rv-exp{margin-top:6px;font-size:.78rem;color:#78350f;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:8px 10px;line-height:1.55;}
.rv-correct{color:var(--accent2);font-weight:700;}.rv-wrong{color:var(--red);font-weight:700;}

/* FOOTER */
footer{margin-top:50px;background:var(--navy);color:white;text-align:center;padding:40px 30px;}
footer h3{margin:10px 0 4px;}
.logo-block{margin-bottom:20px;}
.college-logo{max-width:110px;max-height:110px;background:white;border-radius:50%;padding:8px;}
.designed-by-label{font-size:14px;opacity:0.85;letter-spacing:0.5px;text-transform:uppercase;margin-top:10px;}

@media(max-width:768px){
.container{padding:15px;}
.hero-title{font-size:18px;}
}
