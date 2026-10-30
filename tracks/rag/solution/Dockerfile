# Lab 7: container image for the minirag API.
# Build from the repository root so the course data is in the build context:
#   docker build -f projects/knowledge-assistant/Dockerfile -t minirag .
#   docker run -p 8000:8000 -e MINIRAG_LLM=ollama:llama3.2:3b -e OLLAMA_HOST=http://host.docker.internal:11434 minirag
# (For the reference solution: docker build -f tracks/rag/solution/Dockerfile --build-arg APP_DIR=tracks/rag/solution .)
FROM python:3.12-slim

ARG APP_DIR=projects/knowledge-assistant
WORKDIR /app

# Pin exact versions (pip freeze) before you deploy this anywhere real.
RUN pip install --no-cache-dir fastapi uvicorn

COPY ${APP_DIR}/minirag ./minirag
COPY tracks/rag/data ./data

ENV MINIRAG_DATA=/app/data \
    MINIRAG_DB=/app/.minirag/index.sqlite \
    PYTHONUNBUFFERED=1

RUN useradd --create-home app && mkdir -p /app/.minirag && chown app /app/.minirag
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["python", "-m", "minirag", "serve", "--host", "0.0.0.0", "--port", "8000"]
