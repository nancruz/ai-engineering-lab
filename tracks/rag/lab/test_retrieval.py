import json,math,unittest
from pathlib import Path
from retrieval import metrics,retrieve,eligible,rrf,bm25_scores
ROOT=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_partial_evidence(self):
  m=metrics(["a","x","y"],["a","b"]);self.assertEqual(m,{"recall":.5,"hit":1,"rr":1.,"complete":0})
 def test_duplicate_not_extra_evidence(self):
  m=metrics(["a","a","b"],["a","b"],2);self.assertEqual(m["recall"],1.)
 def test_rank(self):self.assertEqual(metrics(["x","a"],["a"],2)["rr"],.5)
 def test_empty_gold(self):self.assertIsNone(metrics(["x"],[])["recall"])
 def test_invalid_k(self):
  with self.assertRaises(ValueError):metrics([],[],0)
 def test_acl_and_current(self):
  docs=json.loads((ROOT/"data/corpus.json").read_text())
  for q in json.loads((ROOT/"data/dev.json").read_text()):
   for mode in ["keyword","bm25"]:
    by={d["id"]:d for d in docs}
    self.assertTrue(all(eligible(by[h["id"]],q) for h in retrieve(q,docs,mode,99)))
 def test_faulty_is_actually_unsafe(self):
  docs=json.loads((ROOT/"data/corpus.json").read_text());q={"query":"playback emergency capacity setting workers","role":"engineer"}
  self.assertIn("capacity-private",[h["id"] for h in retrieve(q,docs,"faulty",3)])
 def test_rrf(self):self.assertEqual(rrf([["a","b","c"],["c","a","d"]])[0],"a")
 def test_rrf_duplicate(self):self.assertEqual(rrf([["a","a","b"]]),["a","b"])
 def test_bm25_hand_calculation(self):
  docs=[{"id":"a","title":"","text":"red red"},{"id":"b","title":"","text":"blue"}]
  score=bm25_scores("red",docs)["a"]
  expected=math.log(2)*2*2.5/(2+1.5*(.25+.75*2/1.5))
  self.assertAlmostEqual(score,expected)
 def test_empty_corpus(self):self.assertEqual(bm25_scores("x",[]),{})
 def test_fixture_integrity(self):
  docs=json.loads((ROOT/"data/corpus.json").read_text());by={d["id"]:d for d in docs}
  self.assertEqual(len(by),len(docs));families=[]
  for split in ["dev","heldout"]:
   qs=json.loads((ROOT/f"data/{split}.json").read_text());families.append({q["family"] for q in qs})
   for q in qs:self.assertTrue(all(g in by and eligible(by[g],q) for g in q["relevant"]))
  self.assertFalse(families[0]&families[1])
if __name__=="__main__":unittest.main()
