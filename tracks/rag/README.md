# RAG track: code and data

| Folder | What it is |
| --- | --- |
| `data/docs/` | The knowledge base: 24 Markdown runbooks, postmortems, policies and guides for **Lumen**, a fictional streaming platform. Includes archived versions, an SRE-only document and an imported vendor note with a prompt injection. |
| `data/questions.json` | 34 labelled questions (28 dev, 6 test): relevant documents, evidence passages, expected answer facts, and questions that must be abstained on. |
| `starter/` | The `minirag` package with TODOs. Copy it to `projects/knowledge-assistant/` and work there. |
| `solution/` | The same package, finished. |
| `tools/sync.py` | Maintainer script: regenerates `starter/` from `solution/` and the site's data copy. |

The lessons are in `docs/rag/`. Everything here runs on the Python standard library;
real models are optional.
