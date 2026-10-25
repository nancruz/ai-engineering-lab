# AI Engineering Lab

The RAG course is written directly in **HTML**. Open [docs/index.html](docs/index.html) in your browser to start.

## Edit the course

- Lessons: `docs/lessons/*.html`
- Guides: `docs/guides/*.html`
- Course map: `docs/index.html` and `docs/course.html`
- Shared presentation and interactions: `docs/assets/style.css` and `docs/assets/app.js`
- Navigation/session IDs and fictional workbench data: `docs/assets/course-data.js`
- Runnable Python labs: `tracks/rag/lab/`
- Numerical references: `tracks/rag/reference-solutions/`

Edit an HTML page and refresh the browser. There is no Markdown source, generator, package installation or build step for the course. The Python code is the training lab, not a website dependency. Lesson text stays in HTML; search reads those pages directly.

Progress is saved in the browser and can be exported/imported. Commands still run in your development environment. Browser workbenches use the fictional development data and do not call a live model.

## Preview

Open `docs/index.html` directly. For full-text search and normal browser storage behavior, optionally serve the folder using any static server. If Python is already installed:

```bash
python3 -m http.server 8000 --directory docs
```

Then open `http://localhost:8000/`. This serves existing files; it does not build them.

## Publish to GitHub Pages

In repository **Settings → Pages**, select **Deploy from a branch**, choose **main**, select **/docs**, and save. GitHub serves the committed HTML directly. The `.nojekyll` file disables Jekyll processing; no custom build workflow is needed.

Repository visibility and GitHub plan still determine whether Pages is available. This change does not publish the site, change visibility or change your plan.

## Training scope

Three hours per week, eight modules and one evolving knowledge-assistant project. Start with evidence selection, build a real local RAG service, improve retrieval and generation, learn through practical ML experiments, then deploy and operate the service on AWS in the final 12 learning weeks. Keep completed work and continue at the next unfinished session.

The course map, supporting references, checkpoints and all lessons are in `docs/`. Future AI tracks can be added alongside RAG as you begin them. Notion is a planning dashboard; GitHub holds the current materials.
