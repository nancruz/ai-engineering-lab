# Visual RAG course — static HTML

The lesson content remains in its original Markdown files. `scripts/build_course_site.py` generates the HTML interface in `docs/`, including all lessons/guides and the supporting course pages. No lesson text or curriculum is rewritten by the build. Each rendered page offers the original Markdown as a download, and `docs/content-manifest.json` records source hashes.

## What is interactive

- Course map, module/week navigation and expandable one-hour sessions.
- Browser-local session completion, resume position, export/import and reset.
- Full-course search, command copy buttons, print-friendly lessons and responsive navigation.
- Evidence explorer over the existing fictional corpus and development questions. Reference labels stay hidden until revealed. Browser keyword/BM25 retrieval matches the supplied Python reference; it makes no model calls.
- Ranking workbench for the existing A/B/X/Y metric example. Reordering and changing k update Recall, Hit, RR and complete labeled-set coverage.
- Clickable ingestion/query workflow view and an AWS architecture map derived from the existing course.

No API keys, backend, learner accounts, analytics or external JavaScript/CDN are required. Progress stays in this browser; export it before clearing storage or changing devices/origins. It does not sync to the Markdown progress checklist. File:// hosting may restrict persistent storage or clipboard access; localhost/HTTPS is preferred. Code-copy fallback selects the code for manual copying.

All technical exercises still run in your development environment. Interactive examples support those exercises; they do not pretend to execute Python, call an LLM or deploy AWS from the browser.

## Build and check

From repository root:

```bash
python3 -m pip install -r course-site/requirements.txt
python3 -m unittest discover -s tests/site -p 'test*.py' -v
python3 scripts/build_course_site.py
python3 -m http.server 8000 --directory docs
```

Open `http://localhost:8000/`. Or open `docs/index.html` directly for a build-free local view. Python is required only to regenerate files, not to host the finished HTML. Node is required for the browser/Python retrieval parity tests; it is not needed at runtime.

After editing lessons, rebuild `docs/` before committing generated HTML. The workflow also regenerates the artifact from the current Markdown. Keep the generator/styles/JavaScript in `course-site/` and `scripts/`; do not hand-edit generated files.

## Publish to GitHub Pages

The publishing workflow is opt-in: pushes/pull requests build and validate; they do not publish. To publish:

1. Confirm that your GitHub plan supports Pages for the repository's visibility. This repository is private; GitHub Free supports Pages from public repositories, while private-repository Pages needs a supported paid plan. This setup does not change repository visibility or your plan.
2. In the repository, open **Settings → Pages → Build and deployment → Source → GitHub Actions**.
3. Open **Actions → Build visual RAG course → Run workflow**, choose `main`, and enable the `publish` input.
4. Use the deployed URL reported by the workflow. A project site normally uses the `/<repository>/` path; all generated internal links/assets are relative so the same artifact works at that prefix or on a custom domain.

A private source repository does not by itself make a Pages website private. Review the intended audience before publishing. The build explicitly includes only lesson Markdown, approved course code and fictional development fixtures; it excludes `heldout.json`, learner project files, private data and secrets. Do not add private learner material to the publication allowlist.

For a branch-based alternative, select `main` / `docs` as the Pages source and publish the committed generated HTML; `.nojekyll` is included. Choose one publishing route rather than enabling competing workflows.

## Verification

Site tests check the original rendered article text, byte-identical source downloads, relative files/heading links, session IDs, publication exclusions and parity between browser and Python retrieval/metrics. Browser QA covers navigation, completion persistence, same-week next-session links, search and the visual workbenches. A successful build does not mean Pages has been enabled or a live URL exists.

Official setup references: [Pages availability](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) and [custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
