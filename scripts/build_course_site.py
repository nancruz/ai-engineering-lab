#!/usr/bin/env python3
"""Render the existing Markdown course as a portable static learning site."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import unquote
import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / 'tracks/rag'
REPO = 'https://github.com/nancruz/ai-engineering-lab'
MODULES = [f'tracks/rag/lessons/Module_{i:02}.md' for i in range(1, 9)]
LABELS = ['Local RAG service', 'Better retrieval', 'Ingestion & answers', 'Evaluation & gates', 'Evidence-quality model', 'Neural adaptation', 'Deploy on AWS', 'Operate in production']
PHASES = ['Build', 'Retrieve', 'Ground', 'Evaluate', 'Learn', 'Adapt', 'Deploy', 'Operate']

def slug(value, separator='-'):
    # Match existing GitHub-compatible heading anchors, including doubled separators.
    return re.sub(r'[^\w\- ]', '', value.lower()).replace(' ', separator)

def output_name(source):
    if source in MODULES:
        return f'lessons/module-{MODULES.index(source) + 1:02}.html'
    if source == 'tracks/rag/lessons/00-rag-introduction.md':
        return 'lessons/introduction.html'
    if source == 'tracks/rag/README.md':
        return 'course.html'
    if source.startswith('tracks/rag/guides/'):
        return 'guides/' + Path(source).stem + '.html'
    names = {'README.md': 'repository', 'foundations/README.md': 'foundations',
             'projects/README.md': 'projects', 'tracks/rag/lab/README.md': 'lab',
             'tracks/rag/reference-solutions/README.md': 'reference-solutions'}
    return 'resources/' + names.get(source, Path(source).stem.lower().replace('_', '-')) + '.html'

def render(text):
    return markdown.markdown(text, extensions=['fenced_code', 'tables', 'sane_lists', 'toc'],
                             extension_configs={'toc': {'slugify': slug}}, output_format='html')

def relative(page, target):
    return os.path.relpath(target, str(Path(page).parent)).replace(os.sep, '/')

def link(page, target):
    return relative(page, target)

def sidebar(page):
    items = ''
    for i, source in enumerate(MODULES):
        dest = output_name(source)
        current = ' aria-current="page"' if page == dest else ''
        items += f'<a class="module-link" href="{link(page, dest)}"{current}><span class="module-num">{i+1:02}</span><span>{LABELS[i]}<small>{PHASES[i]} · 6 weeks</small></span><span class="module-progress" data-module-progress="{i+1}"></span></a>'
    return f'''<aside class="sidebar" id="sidebar"><a class="brand" href="{link(page,'index.html')}"><span class="brand-icon">ai<span>_</span></span><span>ENGINEERING LAB<small>RAG / LEARNING TRACK</small></span></a>
    <nav aria-label="Course"><a class="nav-home" href="{link(page,'index.html')}">◈ &nbsp; Learning path</a><a class="nav-home" href="{link(page,'lessons/introduction.html')}">↳ &nbsp; Start with RAG</a><p class="nav-label">YOUR BUILD SEQUENCE</p>{items}<p class="nav-label">AT YOUR WORKBENCH</p><a class="nav-home" href="{link(page,'explore.html')}">⌕ &nbsp; Evidence explorer</a><a class="nav-home" href="{link(page,'metrics.html')}">↕ &nbsp; Ranking workbench</a><a class="nav-home" href="{link(page,'guides/production-aws.html')}">◇ &nbsp; AWS field guide</a><a class="nav-home" href="{link(page,'resources/assessment.html')}">✓ &nbsp; Practical checkpoints</a><a class="nav-home" href="{link(page,'course.html')}">≡ &nbsp; Full course guide</a></nav>
    <div class="sidebar-bottom"><div class="progress-caption"><span>Sessions completed</span><strong data-progress-count>0 / 144</strong></div><progress max="144" value="0" data-global-progress aria-label="Completed learning sessions"></progress><button class="text-button" data-open-progress>Progress & backup ↗</button><p>3 HOURS / WEEK · YOUR OWN PACE</p></div></aside>'''

def shell(page, title, content, source=None, module=None):
    base = relative(page, 'assets/') + '/'
    source_link = f'<a href="{link(page,"sources/"+source)}" download>Download lesson Markdown ↗</a>' if source else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="A practical, visual path from RAG evidence to production deployment."><title>{html.escape(title)} · AI Engineering Lab</title><link rel="stylesheet" href="{base}style.css"><script defer src="{base}course-data.js"></script><script defer src="{base}learning.js"></script><script defer src="{base}app.js"></script></head>
<body data-page="{page}" data-module="{module or ''}"><a class="skip-link" href="#main">Skip to lesson</a>{sidebar(page)}<div class="app-shell"><header class="topbar"><button class="icon-button mobile-menu" aria-label="Open navigation" aria-expanded="false" aria-controls="sidebar" id="menu-toggle">☰</button><a class="breadcrumb" href="{link(page,'index.html')}">RAG <span>/</span> {html.escape('Module '+str(module) if module else title)}</a><div class="topbar-actions"><button class="search-button" data-search-open><span>⌕</span> Search the course <kbd>/</kbd></button><button class="icon-button" aria-label="Print this page" data-print>↗</button></div></header>
<main id="main" tabindex="-1">{content}<footer class="page-footer"><span>AI ENGINEERING LAB <span aria-hidden="true">/</span> Learn by building.</span>{source_link}</footer></main></div>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="dialog-head"><h2 id="search-title">Find your next step</h2><button class="icon-button" data-close-dialog aria-label="Close search">×</button></div><label class="sr-only" for="search-input">Search all lessons</label><input id="search-input" type="search" placeholder="Try ‘context’, ‘week 4’ or ‘rollback’" autocomplete="off"><div id="search-results" aria-live="polite"><p class="muted">Search lesson text, sessions and deployment guides.</p></div></dialog>
<dialog id="progress-dialog" aria-labelledby="progress-title"><div class="dialog-head"><h2 id="progress-title">Your learning progress</h2><button class="icon-button" data-close-dialog aria-label="Close progress">×</button></div><p>Saved in this browser only. Export a backup to continue on another device. This tracks your work; it does not grade it.</p><p class="storage-status" role="status"></p><div class="dialog-actions"><button class="button primary" id="export-progress">Export progress</button><label class="button">Import backup<input class="sr-only" type="file" id="import-progress" accept="application/json"></label></div><p id="import-status" role="status"></p><details><summary>Reset this browser’s progress</summary><p>This cannot be undone without a backup.</p><button class="button danger" id="reset-progress">Reset saved progress</button></details></dialog>
<div class="toast" id="toast" role="status" aria-live="polite"></div><noscript><div class="noscript">Lesson content and links remain readable. Enable JavaScript for session controls, search and interactive workbenches.</div></noscript></body></html>'''

def rewrite_links(body, source, page, mapping, files):
    def replace(match):
        url = html.unescape(match.group(1))
        if url.startswith(('https:', 'http:', 'mailto:', '#', 'data:')):
            return match.group(0)
        path, sep, fragment = url.partition('#')
        target = (ROOT / source).parent / unquote(path)
        target = target.resolve()
        try:
            rel = str(target.relative_to(ROOT))
        except ValueError:
            return match.group(0)
        if rel in mapping:
            dest = link(page, mapping[rel])
        elif rel in files:
            dest = link(page, 'files/' + rel)
        else:
            dest = REPO + '/blob/main/' + rel
        return f'href="{html.escape(dest + ("#" + fragment if sep else ""), quote=True)}"'
    return re.sub(r'href="([^"]+)"', replace, body)

def dashboard():
    cards = ''
    for i in range(8):
        cards += f'''<a class="path-card {'production-card' if i>=6 else ''}" href="lessons/module-{i+1:02}.html"><div class="card-top"><span class="phase-tag">{PHASES[i]}</span><span class="card-week">MODULE {i+1:02}</span></div><div class="card-glyph" aria-hidden="true">{['⌘','⌕','▤','✓','◌','⋈','↗','◎'][i]}</div><h3>{LABELS[i]}</h3><div class="card-bottom"><span>6 weeks · 18 hours</span><span aria-hidden="true">↗</span></div><progress max="18" value="0" data-card-progress="{i+1}" aria-label="Module {i+1} session progress"></progress></a>'''
    return f'''<section class="dashboard-hero"><div><p class="eyebrow"><span class="status-dot"></span> PRACTICAL AI ENGINEERING</p><h1>Build it.<br>Understand it.<br><em>Ship it.</em></h1><p class="hero-copy">One knowledge assistant. A clear path from its first piece of evidence to a production deployment.</p><div class="hero-actions"><a class="button primary" data-resume href="lessons/introduction.html">Start with RAG <span>↗</span></a><a class="button" href="course.html">Explore the course</a></div><p class="hero-meta"><span>3 hours / week</span><span>8 modules</span><span>One evolving project</span></p></div><div class="hero-blueprint" aria-label="Course phases"><span class="blueprint-label">THE SYSTEM YOU’LL BUILD</span><div class="blueprint-question">USER QUESTION <span>↘</span></div><div class="blueprint-core"><span class="mini-label">RAG PIPELINE</span><div>Find evidence <span>→</span> Build context <span>→</span> Generate</div></div><div class="blueprint-ground"><span>Versioned sources</span><span>Authorized retrieval</span><span>Traceable answers</span></div><div class="blueprint-release"><span class="status-dot"></span> EVALUATE → DEPLOY → OBSERVE</div><p>Evidence first. Measured improvements. A recoverable release.</p></div></section>
<section class="resume-strip"><div><span class="resume-icon">↳</span><div><p class="eyebrow">YOUR NEXT SESSION</p><h2 data-resume-title>Start with the RAG introduction</h2><p>Already started? Open a session and mark only work you’ve completed.</p></div></div><a class="text-link" data-resume href="lessons/introduction.html">Continue learning →</a></section>
<section class="path-section"><div class="section-heading"><div><p class="eyebrow">THE LEARNING PATH</p><h2>From local experiment to production.</h2></div><p>Build one component. Run it.<br>Inspect what happened. Keep going.</p></div><div class="path-grid">{cards}</div><div class="production-banner"><span>07 → 08</span><p><strong>The final 12 learning weeks focus on production.</strong><br>Deploy on AWS, automate releases, monitor behavior and practice recovery.</p><a href="guides/production-aws.html">Open the field guide ↗</a></div></section>
<section class="workbench-section"><div class="section-heading"><div><p class="eyebrow">MAKE THE CONCEPTS TANGIBLE</p><h2>Open your workbench.</h2></div></div><div class="workbench-grid"><a href="explore.html"><span class="workbench-icon">⌕</span><div><h3>Follow the evidence</h3><p>Inspect the actual fictional corpus, switch retrieval modes and see which sources reach the context.</p><span>Evidence explorer ↗</span></div></a><a href="metrics.html"><span class="workbench-icon">↕</span><div><h3>See what a ranking changes</h3><p>Move the existing example documents, change k and watch Recall, Hit and RR respond.</p><span>Ranking workbench ↗</span></div></a></div></section>'''

def explorer():
    return '''<section class="page-intro"><p class="eyebrow">WORKBENCH / EVIDENCE</p><h1>Follow the evidence.</h1><p>Inspect the same development questions and fictional sources used in the course. This browser view runs the supplied retrieval rules; it does not call a model or replace your terminal exercises.</p></section><div class="explorer-controls panel"><label>Development question<select id="question-select"></select></label><label>Retrieval mode<select id="mode-select"><option value="faulty">Faulty keyword — ignores eligibility</option><option value="keyword" selected>Filtered keyword</option><option value="bm25">BM25 — with eligibility</option></select></label><label>Top-k<select id="k-select"><option>1</option><option>2</option><option selected>3</option><option>5</option></select></label></div><section class="question-panel panel"><p class="eyebrow" id="question-meta"></p><h2 id="question-text"></h2><button class="text-button" id="reveal-labels" aria-expanded="false">Reveal reference labels after your attempt</button><div id="reference-labels" hidden></div></section><div class="explorer-layout"><section><div class="section-heading compact"><h2>Retrieved sources</h2><span id="retrieval-count" class="muted"></span></div><div id="retrieval-results"></div></section><section class="context-panel panel"><p class="eyebrow">CONTEXT INSPECTOR</p><h2 id="source-title">Select a source</h2><div id="source-meta"></div><p id="source-text">Open a retrieved document to inspect its actual evidence and metadata.</p><div id="source-warning" role="status"></div></section></div><details class="panel corpus-browser"><summary>Browse all 27 fictional source documents</summary><label>Filter by title or text<input type="search" id="corpus-search" placeholder="For example: catalog"></label><div id="corpus-list"></div></details>'''

def metrics():
    return '''<section class="page-intro"><p class="eyebrow">WORKBENCH / RANKING</p><h1>A hit isn’t the whole picture.</h1><p>The existing course example needs A for staging and B for production. X and Y are irrelevant. Move documents or change k to inspect the effect on retrieval metrics.</p></section><div class="metrics-layout"><section class="panel"><div class="section-heading compact"><h2>Ranked results</h2><label class="inline-label">Top-k <select id="metric-k"><option>1</option><option>2</option><option selected>3</option><option>4</option></select></label></div><p class="muted">Use the arrow buttons to reorder. Only the first k unique IDs count.</p><ol id="ranked-list" class="ranked-list"></ol><button class="text-button" id="reset-ranking">Restore X, A, Y, B</button></section><section><div class="metric-cards" id="metric-cards" aria-live="polite"></div><div class="panel metric-explanation" id="metric-explanation" aria-live="polite"></div><div class="panel"><h3>Across the three course examples</h3><p>RR values 0.5, 1 and 0 average to MRR = 0.5. RR belongs to one query; MRR averages it across the declared population.</p><p class="muted">Here A and B are complementary and both are required. Relevant sources can be redundant in other datasets; complete labeled-set coverage is not a universal answerability score.</p><a href="lessons/module-01.html#reference--evidence-and-retrieval-metrics">Read the unchanged worked example →</a></div></section></div>'''

def build(output):
    output.mkdir(parents=True, exist_ok=True)
    sources = sorted(p for p in TRACK.rglob('*.md')) + [ROOT/'README.md', ROOT/'foundations/README.md', ROOT/'projects/README.md']
    mapping = {str(p.relative_to(ROOT)): output_name(str(p.relative_to(ROOT))) for p in sources}
    # Publish only explicit course assets. Never copy learner projects, secrets or held-out data.
    assets = [p for folder in ['lab', 'reference-solutions', 'tools'] for p in (TRACK/folder).rglob('*')
              if p.is_file() and p.suffix in ('.py', '.json') and p.name != 'heldout.json']
    files = {str(p.relative_to(ROOT)) for p in assets}
    search, modules, sessions, hashes, content_records = [], [], [], {}, []
    for p in sources:
        source = str(p.relative_to(ROOT)); text = p.read_text(); page = mapping[source]
        hashes[source] = hashlib.sha256(p.read_bytes()).hexdigest()
        body = rewrite_links(render(text), source, page, mapping, files)
        title = re.search(r'^# (.+)', text, re.M).group(1)
        module = MODULES.index(source)+1 if source in MODULES else None
        if module:
            weeks = re.findall(r'^## Week (\d+) — (.+)$', text, re.M)
            for number, week_title in weeks:
                for letter in 'ABC':
                    sid = f'm{module:02}-w{int(number):02}-{letter.lower()}'
                    sessions.append({'id': sid, 'module': module, 'week': int(number), 'letter': letter,
                                     'title': week_title, 'href': page + '#week-' + number + '--' + slug(week_title)})
            modules.append({'id':module, 'title':LABELS[module-1], 'href':page, 'weeks':[int(w[0]) for w in weeks]})
        search.append({'title':title, 'href':page, 'text':re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', body))), 'module':module})
        toc = ''
        if module:
            toc = '<nav class="week-nav" aria-label="Weeks in this module">' + ''.join(f'<a href="#week-{n}--{slug(t)}">{n}<span>{html.escape(t)}</span></a>' for n,t in weeks) + '</nav>'
        content = f'<div class="lesson-heading"><p class="eyebrow">{"MODULE " + str(module).zfill(2) + " / " + PHASES[module-1].upper() if module else "COURSE MATERIAL"}</p><div class="lesson-tools"><button class="text-button" data-expand-all>Expand all</button><button class="text-button" data-collapse-all>Focus view</button></div></div>{toc}<article class="lesson-content" data-source="{source}">{body}</article>'
        target=output/page; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(shell(page,title,content,source,module))
        source_target=output/'sources'/source;source_target.parent.mkdir(parents=True,exist_ok=True);source_target.write_bytes(p.read_bytes())
        content_records.append({'source':source, 'page':page, 'sha256':hashes[source], 'rendered_sha256':hashlib.sha256(body.encode()).hexdigest()})
    for p in assets:
        dest=output/'files'/p.relative_to(ROOT); dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
    corpus=json.loads((TRACK/'lab/data/corpus.json').read_text())
    questions=json.loads((TRACK/'lab/data/dev.json').read_text())
    data={'modules':modules,'sessions':sessions,'search':search,'corpus':corpus,'questions':questions}
    (output/'assets').mkdir(exist_ok=True)
    (output/'assets/course-data.js').write_text('window.COURSE_DATA = '+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';\n')
    for p in (ROOT/'course-site/assets').iterdir():
        if p.is_file():shutil.copyfile(p,output/'assets'/p.name)
    for page,title,content in [('index.html','Learning path',dashboard()),('explore.html','Evidence explorer',explorer()),('metrics.html','Ranking workbench',metrics())]:
        (output/page).write_text(shell(page,title,content))
    (output/'.nojekyll').write_text('')
    (output/'content-manifest.json').write_text(json.dumps({'source_content_unchanged':True,'pages':content_records,'sessions':len(sessions),'source_hashes':hashes},indent=2)+'\n')
    print(f'Built {len(sources)+3} HTML pages and {len(sessions)} sessions in {output}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'docs');args=parser.parse_args();build(args.output.resolve())
