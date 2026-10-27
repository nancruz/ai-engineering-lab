# AI Engineering Lab

Hands-on AI engineering courses, written directly in **HTML**. Open [docs/index.html](docs/index.html) in your browser to see the available courses.

## Courses

| Course | Site | Lab code |
| --- | --- | --- |
| Retrieval-augmented generation (RAG) | `docs/rag/` | `tracks/rag/` |
| Tool-using AI agents | `docs/agents/` | `tracks/agents/` |

`docs/index.html` is the course catalog. Each course lives in its own folder under `docs/` with its own pages, assets and saved progress.

## Add a course

1. Create `docs/<course>/index.html` (and the rest of its pages) and `tracks/<course>/` for its runnable code.
2. Add a card for it in `docs/index.html`, replacing or keeping the “More courses” placeholder.
3. Link back to the catalog from the course's pages (`../index.html` from the course home).
4. Add the folder name to the course list in `tests/site/test_site.py`.

## Edit the RAG course

- Lessons: `docs/rag/lessons/*.html`
- Guides: `docs/rag/guides/*.html`
- Course map: `docs/rag/index.html` and `docs/rag/course.html`
- Shared presentation and interactions: `docs/rag/assets/style.css` and `docs/rag/assets/app.js`
- Navigation/session IDs and fictional workbench data: `docs/rag/assets/course-data.js`
- Runnable Python labs: `tracks/rag/lab/`
- Numerical references: `tracks/rag/reference-solutions/`

Edit an HTML page and refresh the browser. There is no Markdown source, generator, package installation or build step for the course. The Python code is the training lab, not a website dependency. Lesson text stays in HTML; search reads those pages directly.

Progress is saved in the browser and can be exported/imported. Commands still run in your development environment. Browser workbenches use the fictional development data and do not call a live model.

## Edit the agents course

- Lessons: `docs/agents/lessons/*.html`
- Guides and resources: `docs/agents/guides/*.html`, `docs/agents/resources/*.html`
- Course map: `docs/agents/index.html` and `docs/agents/course.html`
- Interactive workbenches: `docs/agents/{loop,tools,guardrails,evals,cost}.html`
- Shared presentation and interactions: `docs/agents/assets/style.css` and `docs/agents/assets/app.js`
- Browser mirror of the lab (loop, validator, gate, grading): `docs/agents/assets/agentlab.js`
- Navigation/session IDs and copies of the lab fixtures: `docs/agents/assets/course-data.js`
- Runnable Python lab (standard library, scripted models, optional Ollama adapter): `tracks/agents/lab/`, mirrored read-only under `docs/agents/files/tracks/agents/lab/` for linking

The workbenches never call a model. `tests/site/test_site.py` runs `agentlab.js` in Node and checks it returns exactly what the Python lab returns, and that `course-data.js` holds the same fixtures as `tracks/agents/lab/data/`. If you change a fixture or the lab, update the copies and run the tests.

Each week ends with an ungraded quick check (`<div class="quick-check">` with one `data-correct` option). Answers are saved in the browser with session progress.

## Preview

Open `docs/index.html` directly. For full-text search and normal browser storage behavior, optionally serve the folder using any static server. If Python is already installed:

```bash
python3 -m http.server 8000 --directory docs
```

Then open `http://localhost:8000/`. This serves existing files; it does not build them.

## Publish to GitHub Pages

In repository **Settings → Pages**, select **Deploy from a branch**, choose **main**, select **/docs**, and save. GitHub serves the committed HTML directly: the catalog at `https://<user>.github.io/ai-engineering-lab/` and each course under its folder, e.g. `/ai-engineering-lab/rag/`. The `.nojekyll` file disables Jekyll processing; no custom build workflow is needed.

Repository visibility and GitHub plan still determine whether Pages is available. This change does not publish the site, change visibility or change your plan.

## Training scope

Three hours per week, eight modules and one evolving knowledge-assistant project. Start with evidence selection, build a real local RAG service, improve retrieval and generation, learn through practical ML experiments, then deploy and operate the service on AWS in the final 12 learning weeks. Keep completed work and continue at the next unfinished session.

The RAG course map, supporting references, checkpoints and all lessons are in `docs/rag/`. The agents course (seven modules, 28 weeks, same three-hours-a-week rhythm) is in `docs/agents/` and builds an ops agent on the RAG course's fictional corpus. Future AI tracks are added alongside them (see **Add a course**). Notion is a planning dashboard; GitHub holds the current materials.
