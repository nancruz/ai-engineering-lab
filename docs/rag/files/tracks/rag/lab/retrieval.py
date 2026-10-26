"""Inspectable retrieval reference, no LLM calls or third-party dependencies."""
from collections import Counter
import math,re

def tokens(s): return re.findall(r"[a-z0-9]+",s.lower())
def eligible(doc,q):
    return q["role"] in doc["roles"] and (not q.get("current_only",True) or doc["status"]=="current")
def unique(ids): return list(dict.fromkeys(ids))
def metrics(ranked,relevant,k=3):
    if k<1: raise ValueError("k must be positive")
    gold=set(relevant)
    if not gold: return {"recall":None,"hit":None,"rr":None,"complete":None}
    found=unique(ranked)[:k]
    ranks=[i+1 for i,d in enumerate(found) if d in gold]
    overlap=len(set(found)&gold)
    return {"recall":overlap/len(gold),"hit":int(bool(ranks)),
            "rr":1/min(ranks) if ranks else 0.,"complete":int(overlap==len(gold))}
def bm25_scores(query,docs,k1=1.5,b=.75):
    if k1<=0 or not 0<=b<=1: raise ValueError("invalid BM25 settings")
    if not docs:return {}
    tf={d["id"]:Counter(tokens(d["title"]+" "+d["text"])) for d in docs}
    avg=sum(sum(x.values()) for x in tf.values())/len(docs)
    if not avg:return {d["id"]:0. for d in docs}
    terms=set(tokens(query));scores={}
    for ident,counts in tf.items():
        length=sum(counts.values()); score=0.
        for t in terms:
            f=counts[t]
            if not f:continue
            df=sum(t in c for c in tf.values())
            idf=math.log(1+(len(docs)-df+.5)/(df+.5))
            score+=idf*f*(k1+1)/(f+k1*(1-b+b*length/avg))
        scores[ident]=score
    return scores

def retrieve(q,docs,mode="bm25",k=3):
    if mode not in {"faulty","keyword","bm25"}:raise ValueError("unknown mode")
    candidates=docs if mode=="faulty" else [d for d in docs if eligible(d,q)]
    if mode=="bm25":scores=bm25_scores(q["query"],candidates)
    else:
        terms=set(tokens(q["query"]))
        scores={d["id"]:len(terms & set(tokens(d["title"]+" "+d["text"]))) for d in candidates}
    ordered=sorted(scores,key=lambda d:(-scores[d],d))
    return [{"id":d,"score":scores[d]} for d in ordered if scores[d]>0][:k]

def rrf(rankings,c=60):
    if c<0:raise ValueError("c must be nonnegative")
    scores={}
    for ranking in rankings:
        for rank,ident in enumerate(unique(ranking),1):
            scores[ident]=scores.get(ident,0.)+1/(c+rank)
    return sorted(scores,key=lambda d:(-scores[d],d))
