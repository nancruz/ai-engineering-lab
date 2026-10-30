# minirag: reference solution

The finished version of the RAG course labs. Same layout as `tracks/rag/starter/`; the
code between `# LABn-BEGIN` and `# LABn-END` markers is what each lab asks you to write.

Do the lab in your own copy first (`projects/knowledge-assistant/`), then compare.

```bash
cd tracks/rag/solution
python3 -m unittest discover -s tests -t .     # all lab tests
python3 -m minirag ask "What is the current production timeout for catalog API requests?"
```

Maintainers: after editing anything here, regenerate the starter with
`python3 tracks/rag/tools/sync.py` and run `python3 -m unittest discover -s tests/site`.
