# Environment and dependency progression

Use a project-local virtual environment and pin the versions you actually test. Commands in lessons assume a Unix-like shell and Python 3.10+; on Windows adapt the launcher/path conventions. No basic Python lessons are required.

| Phase | Dependencies introduced | Account/hardware needs |
| --- | --- | --- |
| Weeks 1–3 | Python standard library; supplied search/evaluation/tests | Local machine only |
| Week 4 | Ollama + installed `llama3.2:3b` or documented Bedrock adapter alternative | Suitable local RAM/storage, or your cloud model access |
| Weeks 5–6 | FastAPI, Uvicorn, pytest and HTTP test client dependencies | Local loopback API |
| Retrieval | Sentence Transformers and compatible PyTorch/tokenizer libraries | Real encoder/reranker downloads and bounded inference |
| Applied ML | NumPy, scikit-learn | CPU training on the small evidence dataset |
| Neural adaptation | PyTorch, compatible CrossEncoder trainer dependencies | Bounded real training; optional budgeted accelerator if local hardware cannot complete it |
| Persistence/containers | Docker/Compose, PostgreSQL+pgvector, psycopg/pgvector adapter, migration tooling | Local container runtime |
| Production | boto3/botocore, maintained JWT library, Terraform, AWS CLI and GitHub Actions | Sandbox account, region/model access, domain/TLS and a cost/teardown plan |

Add dependencies only when introduced. Save model revisions, image digests, seeds and platform/architecture with your runs. Changing providers/models, preprocessing or versions can change results and calls for a new compatible evaluation.

The supplied standard-library helpers are tested independently of your later application. Cloud infrastructure, adapters and application targets are implementation tasks; their compatibility must be checked in your actual environment. Training references use generated data for mechanics checks and do not establish production model quality.
