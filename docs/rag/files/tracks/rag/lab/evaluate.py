import argparse,json,hashlib
from pathlib import Path
from statistics import mean
from retrieval import retrieve,metrics,eligible
ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=["faulty","keyword","bm25"],default="faulty")
    p.add_argument("--split",choices=["dev","heldout"],default="dev");p.add_argument("--k",type=int,default=3)
    p.add_argument("--out",default=None);a=p.parse_args()
    if a.k<1:p.error("k must be positive")
    raw=(ROOT/"data/corpus.json").read_bytes();docs=json.loads(raw)
    queries=json.loads((ROOT/f"data/{a.split}.json").read_text());byid={d["id"]:d for d in docs}
    rows=[]
    for q in queries:
        hits=retrieve(q,docs,a.mode,a.k);ids=[x["id"] for x in hits]
        rows.append({"id":q["id"],"family":q["family"],"query":q["query"],"slice":q["slice"],
        "expected":q["expected"],"retrieved":hits,"metrics":metrics(ids,q["relevant"],a.k),
        "unauthorized":[i for i in ids if q["role"] not in byid[i]["roles"]],
        "stale":[i for i in ids if q.get("current_only",True) and byid[i]["status"]!="current"]})
    scored=[r for r in rows if r["metrics"]["recall"] is not None]
    result={"mode":a.mode,"k":a.k,"split":a.split,"corpus_sha256":hashlib.sha256(raw).hexdigest(),
    "n_queries":len(rows),"n_answerable":len(scored),"n_abstention_cases":len(rows)-len(scored),
    "mean_metrics":{m:mean(r["metrics"]["rr" if m == "mrr" else m] for r in scored) if scored else None for m in ["recall","hit","mrr","complete"]},
    "queries_with_unauthorized":sum(bool(r["unauthorized"]) for r in rows),
    "queries_with_stale":sum(bool(r["stale"]) for r in rows),"rows":rows,
    "limitations":"Synthetic retrieval experiment. No LLM calls. Empty-gold queries excluded from recall; no automatic claim of abstention correctness."}
    output=json.dumps(result,indent=2)
    if a.out:Path(a.out).write_text(output+"\n")
    print(output)
if __name__=="__main__":main()
