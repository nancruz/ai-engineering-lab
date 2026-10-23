"""Exploratory paired bootstrap by intent family; does not fix benchmark bias."""
import argparse,json,random
from statistics import mean
p=argparse.ArgumentParser();p.add_argument("baseline");p.add_argument("candidate");a=p.parse_args()
b=json.load(open(a.baseline));c=json.load(open(a.candidate))
if b["corpus_sha256"]!=c["corpus_sha256"] or b["k"]!=c["k"] or b["split"]!=c["split"]:
 raise ValueError("comparison requires matching corpus, k and split")
br={r["id"]:r for r in b["rows"]};cr={r["id"]:r for r in c["rows"]}
if br.keys()!=cr.keys():raise ValueError("query sets differ")
groups={}
for ident,x in br.items():
 y=cr[ident]
 if x["family"]!=y["family"] or x["query"]!=y["query"]:raise ValueError("query identity changed")
 if x["metrics"]["recall"] is not None:
  groups.setdefault(x["family"],[]).append(y["metrics"]["recall"]-x["metrics"]["recall"])
values=[mean(v) for v in groups.values()]
if len(values)<2:raise ValueError("need at least two answerable families")
rng=random.Random(7);samples=sorted(mean(rng.choices(values,k=len(values))) for _ in range(2000))
print(json.dumps({"mean_family_recall_delta":mean(values),"families":len(values),
 "exploratory_percentile_interval":[samples[49],samples[1949]],
 "warning":"Small synthetic family sample: this is an exercise in paired analysis, not evidence of population benefit."},indent=2))
