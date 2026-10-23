"""Display practice questions without revealing reference labels. No model calls."""
import argparse
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "lab" / "data"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="+", default=["q02", "q03", "q13", "q14", "q16", "q17"])
    parser.add_argument("--check", action="store_true", help="Reveal labels after your own attempt")
    args = parser.parse_args()
    questions = {q["id"]: q for q in json.loads((DATA / "dev.json").read_text())}
    for ident in args.ids:
        if ident not in questions:
            parser.error(f"Unknown development question: {ident}")
        q = questions[ident]
        print(f"\n{ident}: {q['query']}\nReader: {q['role']} | current only: {q['current_only']}")
        if args.check:
            print(f"Reference evidence: {q['relevant']} | expected behavior: {q['expected']}")

if __name__ == "__main__":
    main()
