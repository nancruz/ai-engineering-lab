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

- Pages: `docs/rag/index.html`, `docs/rag/setup.html`, `docs/rag/modules/*.html` (one per module: a **Learn** part with interactive widgets and a **Build** part with the lab), `docs/rag/capstone.html`, `docs/rag/reference.html`
- Presentation and widgets: `docs/rag/assets/style.css` and `docs/rag/assets/app.js`
- Browser mirror of the Python algorithms (tokenizer, BM25, chunking, packing, metrics, RRF): `docs/rag/assets/raglab.js`
- Knowledge base and labelled questions: `tracks/rag/data/` (24 Markdown documents, 34 questions); the widgets read a copy in `docs/rag/assets/course-data.js`
- Lab code: `tracks/rag/solution/` is the finished `minirag` package; code between `# LABn-BEGIN` and `# LABn-END` is what the learner writes. `tracks/rag/starter/` is generated from it.

After changing the solution or the data, run `python3 tracks/rag/tools/sync.py` to regenerate the starter and `course-data.js`. `tests/site/test_site.py` fails if either is stale, runs every lab's tests against the solution, checks that each lab passes once only it and the earlier labs are written, and checks that `raglab.js` returns exactly what the Python code returns.

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

**RAG** (`docs/rag/`): seven modules plus a capstone, about 30–35 hours. Each module is one focused page with interactive widgets that run on a fictional streaming company's knowledge base, followed by a hands-on lab in one growing Python package (`minirag`) with starter code, tests and a reference solution: keyword search, embeddings, chunking, grounded generation, evaluation, hybrid search and reranking, and shipping it as a service. Everything runs on the Python standard library; local or hosted models plug in with a flag. There are no quizzes or written assignments.

**Agents** (`docs/agents/`): seven modules, 28 weeks at three hours a week, building an ops agent for the same fictional platform. Its lab ships its own small retriever and corpus.

Future AI tracks are added alongside them (see **Add a course**). Notion is a planning dashboard; GitHub holds the current materials.
