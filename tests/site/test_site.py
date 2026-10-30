"""Optional standard-library checks for the directly editable static HTML courses."""
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'docs'
RAG=DOCS/'rag'
TRACK=ROOT/'tracks/rag'
SOLUTION=TRACK/'solution'

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.add(attrs['id'])
        value=attrs.get('src') if tag=='script' else attrs.get('href') if tag in ('a','link') else None
        if value:self.links.append(value)

def load_sync():
    spec=importlib.util.spec_from_file_location('rag_sync',TRACK/'tools/sync.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

class StaticCourseChecks(unittest.TestCase):
    def test_html_links_and_assets_resolve_without_source_files(self):
        pages={}
        for path in DOCS.rglob('*.html'):
            page=Page();page.feed(path.read_text());pages[path.resolve()]=page
        self.assertEqual(len(pages),31)
        for path,page in pages.items():
            for href in page.links:
                link=urlsplit(href)
                if link.scheme or link.netloc:continue
                self.assertFalse(href.startswith('/'))
                target=(path.parent/unquote(link.path)).resolve() if link.path else path
                self.assertTrue(target.is_file(),f'{path}: {href}')
                if link.fragment and target in pages:self.assertIn(unquote(link.fragment),pages[target].ids)
    def test_no_markdown_or_build_artifacts_in_course(self):
        self.assertFalse(list(DOCS.rglob('*.md')))
        self.assertFalse((ROOT/'scripts/build_course_site.py').exists())
        self.assertFalse((ROOT/'course-site').exists())
        self.assertFalse((ROOT/'.github/workflows/course-site.yml').exists())
        self.assertFalse((DOCS/'sources').exists())
        self.assertFalse((DOCS/'assets').exists())
    def test_catalog_lists_each_course_and_courses_link_back(self):
        catalog=Page();catalog.feed((DOCS/'index.html').read_text())
        courses=sorted(p.parent.name for p in DOCS.glob('*/index.html'))
        self.assertEqual(courses,['agents','rag'])
        for course in courses:
            self.assertIn(f'{course}/index.html',catalog.links)
            for path in (DOCS/course).rglob('*.html'):
                page=Page();page.feed(path.read_text())
                back=[h for h in page.links if h.endswith('index.html') and (path.parent/h).resolve()==(DOCS/'index.html').resolve()]
                self.assertTrue(back,f'{path} has no link to the course catalog')

def rag_node(script,payload=None,lib='docs/rag/assets/raglab.js'):
    js=("const L=require('./"+lib+"');require('./docs/rag/assets/course-data.js');const D=globalThis.RAG_DATA;"
        "const x=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(("+script+")(L,D,x)));")
    return json.loads(subprocess.check_output(['node','-e',js],input=json.dumps(payload).encode(),cwd=ROOT))

sys.path.insert(0,str(SOLUTION))
from minirag import chunking, evaluation, generation, hybrid, lexical, retrieval, text  # noqa: E402
from minirag.documents import load_documents, load_questions  # noqa: E402
from minirag.chunking import chunk_document, chunk_documents  # noqa: E402

CONFIGS=[('document',800,0),('fixed',300,0),('fixed',300,100),('fixed',120,40),('paragraph',600,0),('paragraph',250,50),
         ('headings',800,0),('headings',400,0),('headings',150,0)]

def ranked(pairs):
    """Order (id, score) pairs so last-bit float differences between Python and JS cannot swap ties."""
    return sorted([[i,round(s,9)] for i,s in pairs],key=lambda r:(-r[1],r[0]))

class RagCourseChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs=load_documents(TRACK/'data/docs');cls.questions=load_questions(TRACK/'data/questions.json')
    def test_module_pages_have_learn_and_build_parts_and_no_quizzes(self):
        pages=sorted((RAG/'modules').glob('*.html'))
        self.assertEqual([p.stem for p in pages],['01-keyword-search','02-embeddings','03-chunking','04-generation','05-evaluation','06-better-retrieval','07-ship-it'])
        for n,path in enumerate(pages,1):
            html=path.read_text()
            for marker in ('id="learn"','id="build"','class="done-box"',f'data-lab="{n}"','data-widget="','class="try"'):
                self.assertIn(marker,html,path)
            self.assertIn(f'tests.test_lab{n}_',html,path)
        for path in RAG.rglob('*.html'):self.assertNotIn('quick-check',path.read_text())
    def test_every_widget_on_a_page_exists_in_app_js(self):
        app=(RAG/'assets/app.js').read_text();defined=set(re.findall(r'widgets\.(\w+) = ',app))
        used={w for p in RAG.rglob('*.html') for w in re.findall(r'data-widget="(\w+)"',p.read_text())}
        self.assertTrue(used);self.assertLessEqual(used,defined)
    def test_lab_commands_on_pages_exist(self):
        tests={p.stem for p in (SOLUTION/'tests').glob('test_lab*.py')}
        for path in RAG.rglob('*.html'):
            for name in re.findall(r'tests\.(test_lab\w+)',path.read_text()):self.assertIn(name,tests,path)
    def test_site_data_and_starter_are_in_sync_with_the_track(self):
        sync=load_sync()
        self.assertEqual((RAG/'assets/course-data.js').read_text(encoding='utf-8'),sync.course_data(),'run python3 tracks/rag/tools/sync.py')
        with tempfile.TemporaryDirectory() as tmp:
            sync.build(Path(tmp)/'starter')
            fresh={p.relative_to(Path(tmp)/'starter'):p.read_bytes() for p in (Path(tmp)/'starter').rglob('*') if p.is_file()}
        committed={p.relative_to(TRACK/'starter'):p.read_bytes() for p in (TRACK/'starter').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        self.assertEqual(sorted(fresh),sorted(committed),'run python3 tracks/rag/tools/sync.py')
        for name in fresh:self.assertEqual(fresh[name],committed[name],f'{name} is stale: run python3 tracks/rag/tools/sync.py')
    def test_questions_point_at_real_documents_and_evidence(self):
        bodies={d.id:d.body.lower() for d in self.docs}
        self.assertEqual(len({q['id'] for q in self.questions}),len(self.questions))
        for q in self.questions:
            self.assertEqual(q['expected']=='abstain',not q['relevant'],q['id'])
            for r in q['relevant']:self.assertIn(r,bodies,q['id'])
            for e in q.get('evidence',[]):self.assertTrue(any(e.lower() in bodies[r] for r in q['relevant']),(q['id'],e))
    def run_tests(self,folder,env=None):
        return subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-t','.'],cwd=folder,capture_output=True,text=True,env=env)
    def test_solution_passes_every_lab(self):
        result=self.run_tests(SOLUTION)
        self.assertEqual(result.returncode,0,result.stderr[-3000:])
    def test_each_lab_passes_once_it_and_the_earlier_labs_are_written(self):
        sync=load_sync();env={**os.environ,'MINIRAG_DATA':str(TRACK/'data')}
        for n in range(1,8):
            later=''.join(str(i) for i in range(n+1,8)) or 'X'
            sync.BEGIN=re.compile(r'^(\s*)# LAB(['+later+r'])-BEGIN\s*$');sync.END=re.compile(r'^\s*# LAB(['+later+r'])-END\s*$')
            with tempfile.TemporaryDirectory() as tmp:
                sync.build(Path(tmp)/'s')
                test=next((Path(tmp)/'s/tests').glob(f'test_lab{n}_*.py')).stem
                result=subprocess.run([sys.executable,'-m','unittest',f'tests.{test}'],cwd=Path(tmp)/'s',capture_output=True,text=True,env=env)
                self.assertEqual(result.returncode,0,f'lab {n} needs a later lab:\n'+result.stderr[-2000:])
    def test_starter_tests_fail_only_on_todos(self):
        result=self.run_tests(TRACK/'starter')
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn('AssertionError',result.stderr)
        for n in range(1,8):self.assertIn(f'NotImplementedError: Lab {n}:',result.stderr)
    def test_tokenizer_and_prompt_constants_match_the_browser(self):
        got=rag_node('(L,D,x)=>({stop:[...L.STOPWORDS].sort(),system:L.SYSTEM_PROMPT,abstain:L.ABSTAIN,tokens:x.map(t=>L.tokenize(t))})',
                 [d.title+'\n'+d.body for d in self.docs]+[q['question'] for q in self.questions])
        self.assertEqual(got['stop'],sorted(text.STOPWORDS))
        self.assertEqual(got['system'],generation.SYSTEM_PROMPT);self.assertEqual(got['abstain'],generation.ABSTAIN)
        self.assertEqual(got['tokens'],[text.tokenize(d.title+'\n'+d.body) for d in self.docs]+[text.tokenize(q['question']) for q in self.questions])
    def test_chunking_widget_matches_the_python_chunker(self):
        got=rag_node('(L,D,x)=>x.map(([s,n,o])=>D.docs.map(d=>L.chunkDocument(d,s,n,o).map(c=>[c.id,c.start,c.end,c.heading])))',CONFIGS)
        for config,result in zip(CONFIGS,got):
            self.assertEqual(result,[[[c.id,c.start,c.end,c.heading] for c in chunk_document(d,*config)] for d in self.docs],config)
    def test_search_widgets_match_the_python_bm25_and_filters(self):
        cases=[(s,n,o,k1,b) for s,n,o in CONFIGS for k1,b in [(1.5,.75),(0,0),(3,1)]]
        got=rag_node("""(L,D,x)=>x.cases.map(([s,n,o,k1,b])=>{const ix=new L.BM25Index(L.chunkDocuments(D.docs,s,n,o),k1,b);
            return D.questions.map(q=>[L.retrieve(ix,q.question,500,q.role).map(h=>[h.id,h.score]),L.retrieve(ix,q.question,500,'engineer',true,false).length])})""",{'cases':cases})
        for (s,n,o,k1,b),result in zip(cases,got):
            index=lexical.BM25Index(chunk_documents(self.docs,s,n,o),k1,b)
            for q,(hits,unfiltered) in zip(self.questions,result):
                expected=[[c.id,score] for c,score in index.search(q['question'],500,allow=lambda c:retrieval.allowed(c,q['role']))]
                self.assertEqual(ranked(hits),ranked(expected),(s,n,o,k1,b,q['id']))
                self.assertEqual(unfiltered,len(index.search(q['question'],500)))
    def test_metric_fusion_and_packing_widgets_match_python(self):
        lists=[(['X','A','Y'],['A','B']),(['A','A','B','C'],['B','C']),(['X','Y'],['A']),(['A'],[]),(['B','C','A','D','E'],['A','E','F'])]
        got=rag_node("""(L,D,x)=>({m:x.lists.map(([r,g])=>[1,2,3,5].map(k=>[L.hitAtK(r,g,k),L.recallAtK(r,g,k),L.reciprocalRank(r,g,k),L.ndcgAtK(r,g,k)])),
            rrf:x.rrf.map(([ls,c])=>L.rrf(ls,c).map(f=>[f.id,f.score])),
            ev:L.evidenceRecall(['The deadline is 800 MS total.','Retry once.'],['800 ms total','retry once','circuit breaker']),
            pack:x.budgets.map(b=>{const ch=L.chunkDocuments(D.docs,'headings',800,0);const ix=new L.BM25Index(ch);
                return D.questions.map(q=>{const p=L.packContext(L.retrieve(ix,q.question,8,q.role),b);return [p.selected.map(h=>h.id),p.dropped.map(h=>h.id),L.buildPrompt(q.question,p.selected).user]})})})""",
                 {'lists':lists,'rrf':[([['A','B','C'],['C','A','D']],60),([['A','A','B'],['B','C']],0),([['b'],['a'],[]],60)],'budgets':[0,200,700,1500]})
        for (r,g),row in zip(lists,got['m']):
            self.assertEqual(row,[[evaluation.hit_at_k(r,g,k),evaluation.recall_at_k(r,g,k),evaluation.reciprocal_rank(r,g,k),evaluation.ndcg_at_k(r,g,k)] for k in [1,2,3,5]])
        for (ls,c),fused in zip([([['A','B','C'],['C','A','D']],60),([['A','A','B'],['B','C']],0),([['b'],['a'],[]],60)],got['rrf']):
            self.assertEqual(ranked(fused),ranked(hybrid.rrf(ls,c)))
        self.assertAlmostEqual(got['ev'],evaluation.evidence_recall(['The deadline is 800 MS total.','Retry once.'],['800 ms total','retry once','circuit breaker']))
        r=retrieval.LexicalRetriever(chunk_documents(self.docs))
        for budget,rows in zip([0,200,700,1500],got['pack']):
            for q,(sel,drop,user) in zip(self.questions,rows):
                selected,dropped=generation.pack_context(r.retrieve(q['question'],8,q['role']),budget)
                self.assertEqual((sel,drop),([h.chunk.id for h in selected],[h.chunk.id for h in dropped]),(budget,q['id']))
                if selected:self.assertEqual(user,generation.build_messages(q['question'],selected)[1]['content'])

class FakeModelServer(BaseHTTPRequestHandler):
    """Answers like Ollama, OpenAI-compatible servers and Anthropic, recording what it received."""
    seen=[]
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));FakeModelServer.seen.append((self.path,{k.lower():v for k,v in self.headers.items()},body))
        replies={'/api/chat':{'message':{'role':'assistant','content':'ollama says [S1]'}},
                 '/api/embed':{'embeddings':[[3.0,4.0]]*len(body.get('input',[]))},
                 '/v1/chat/completions':{'choices':[{'message':{'content':'openai says [S1]'}}]},
                 '/v1/embeddings':{'data':[{'index':i,'embedding':[0.0,2.0]} for i in range(len(body.get('input',[])))]},
                 '/v1/messages':{'content':[{'type':'text','text':'anthropic says [S1]'}]}}
        data=json.dumps(replies[self.path]).encode();self.send_response(200);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def log_message(self,*a):pass

class ModelAdapterChecks(unittest.TestCase):
    def test_adapters_send_and_read_the_documented_shapes(self):
        from minirag.llm import AnthropicLLM, OllamaLLM, OpenAICompatLLM
        from minirag.embeddings import OllamaEmbedder, OpenAIEmbedder
        server=HTTPServer(('127.0.0.1',0),FakeModelServer);threading.Thread(target=server.serve_forever,daemon=True).start()
        base=f'http://127.0.0.1:{server.server_address[1]}';FakeModelServer.seen.clear()
        messages=[{'role':'system','content':'rules'},{'role':'user','content':'question'}]
        try:
            self.assertEqual(OllamaLLM('m',host=base).complete(messages),'ollama says [S1]')
            self.assertEqual(OpenAICompatLLM('m',base_url=base+'/v1',api_key='k').complete(messages),'openai says [S1]')
            self.assertEqual(AnthropicLLM('m',api_key='k',base_url=base).complete(messages),'anthropic says [S1]')
            self.assertEqual(OllamaEmbedder('nomic-embed-text',host=base).embed_documents(['a','b']),[[0.6,0.8],[0.6,0.8]])
            self.assertEqual(OpenAIEmbedder('m',base_url=base+'/v1',api_key='k').embed_query('a'),[0.0,1.0])
        finally:
            server.shutdown();server.server_close()
        (p1,_,ollama),(p2,h2,openai),(p3,h3,anthropic),(p4,_,embed),(p5,_,_)=FakeModelServer.seen
        self.assertEqual((ollama['stream'],ollama['messages']),(False,messages))
        self.assertEqual(h2['authorization'],'Bearer k');self.assertEqual(openai['messages'],messages)
        self.assertEqual((h3['x-api-key'],h3['anthropic-version']),('k','2023-06-01'))
        self.assertEqual((anthropic['system'],anthropic['messages']),('rules',messages[1:]));self.assertIn('max_tokens',anthropic)
        self.assertEqual(embed['input'],['search_document: a','search_document: b'])

AGENTS=DOCS/'agents'
AGENT_LAB=ROOT/'tracks/agents/lab'
sys.path.insert(0,str(AGENT_LAB))
import agent as agent_lab, guard as guard_lab, grading as grading_lab, schema as schema_lab
from itertools import combinations, product

def agents_data():
    value=(AGENTS/'assets/course-data.js').read_text().split('window.COURSE_DATA = ',1)[1]
    return json.loads(value.rstrip(';\n'))

def node(script,payload):
    js="const l=require('./docs/agents/assets/agentlab.js'),x=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(("+script+")(l,x)));"
    return json.loads(subprocess.check_output(['node','-e',js],input=json.dumps(payload).encode(),cwd=ROOT))

class AgentsCourseChecks(unittest.TestCase):
    def test_sessions_cover_28_weeks_in_seven_modules(self):
        data=agents_data()
        self.assertEqual(len({s['id'] for s in data['sessions']}),84)
        self.assertEqual({s['week'] for s in data['sessions']},set(range(1,29)))
        self.assertEqual([m['id'] for m in data['modules']],list(range(1,8)))
        self.assertTrue(all('text' not in page for page in data['search']))
    def test_lesson_pages_have_three_sessions_per_week_and_one_answer_per_quick_check(self):
        ids=[]
        for path in sorted((AGENTS/'lessons').glob('module-*.html')):
            html=path.read_text()
            self.assertEqual(html.count('<h3 id="session-a'),4,path)
            self.assertEqual(html.count('<h3 id="session-c'),4,path)
            checks=html.split('class="quick-check"')[1:]
            self.assertEqual(len(checks),4,path)
            for chunk in checks:
                block=chunk.split('</div>',1)[0]
                self.assertEqual(block.count('data-correct'),1,path)
                ids.append(block.split('data-check-id="',1)[1].split('"',1)[0])
        self.assertEqual(len(ids),len(set(ids)))
    def test_browser_fixtures_match_the_lab(self):
        data=agents_data()
        lab=lambda n:json.loads((AGENT_LAB/'data'/n).read_text())
        self.assertEqual(data['corpus'],lab('corpus.json'))
        for key,name in [('world','world.json'),('tools','tools.json'),('tasks','tasks.json'),('scenarios','guard_scenarios.json'),('trials','trials.json')]:
            self.assertEqual(data[key],lab(name),name)
        for src in AGENT_LAB.rglob('*'):
            if src.is_file() and '__pycache__' not in src.parts:
                self.assertEqual((AGENTS/'files/tracks/agents/lab'/src.relative_to(AGENT_LAB)).read_bytes(),src.read_bytes(),src)
    def test_loop_workbench_matches_the_python_agent(self):
        data=agents_data()
        cases=[{'task':t['id'],'o':{'model':m,'action_gate':g,'detect_repeats':r,'retry_transient':rt,'fault':f,'max_steps':n}}
               for t in data['tasks'] for m in ['careful','eager'] for g in [True,False] for r in [True,False] for rt in [True,False]
               for f in ['none','timeout_once','timeout_always'] for n in [1,3,6,8]]
        got=node('(l,x)=>x.cases.map(c=>l.runAgent(x.data,c.task,c.o))',{'cases':cases,'data':data})
        for case,record in zip(cases,got):
            expected=json.loads(json.dumps(agent_lab.run_agent(case['task'],case['o'])))
            self.assertEqual(record,expected,case)
    def test_tool_workbench_matches_the_python_validator(self):
        data=agents_data()
        cases=[{'schema':t['input_schema'],'args':p['args']} for t in data['tools'] for p in data['arg_presets'][t['name']]]
        got=node('(l,x)=>({v:x.cases.map(c=>l.validate(c.schema,c.args)),lint:x.tools.map(t=>l.lintTool(t))})',{'cases':cases,'tools':data['tools']})
        self.assertEqual(got['v'],[schema_lab.validate(c['schema'],c['args']) for c in cases])
        self.assertEqual(got['lint'],[schema_lab.lint_tool(t) for t in data['tools']])
        self.assertTrue(any(got['v']) and not all(got['v']))
    def test_guard_workbench_matches_the_python_gate(self):
        data=agents_data()
        subsets=[list(c) for k in range(len(guard_lab.DEFENSES)+1) for c in combinations(guard_lab.DEFENSES,k)]
        got=node('(l,x)=>x.subsets.map(d=>x.scenarios.map(s=>l.gate(s,d)))',{'subsets':subsets,'scenarios':data['scenarios']})
        self.assertEqual(got,[[guard_lab.gate(s,d) for s in data['scenarios']] for d in subsets])
    def test_grader_workbench_matches_the_python_estimators(self):
        data=agents_data()
        cases=[{'g':{'end_state':a,'no_forbidden_attempt':b,'cites_required':c,'max_steps':m},'k':k}
               for a,b,c in product([True,False],repeat=3) for m in [0,4,8] for k in range(1,7)]
        got=node('(l,x)=>x.cases.map(c=>l.report(x.trials,c.g,c.k,3))',{'cases':cases,'trials':data['trials']})
        for case,r in zip(cases,got):
            e=grading_lab.report(case['g'],case['k'],3.0)
            self.assertAlmostEqual(r['mean_pass_at_k'],e['mean_pass_at_k'],places=12)
            self.assertAlmostEqual(r['mean_pass_hat_k'],e['mean_pass_hat_k'],places=12)
            self.assertEqual([(t['passed'],t['failures']) for t in r['tasks']],[(t['passed'],t['failures']) for t in e['tasks']])
    def test_cost_model_grows_quadratically_and_compaction_caps_it(self):
        got=node("""(l)=>{const p={steps:10,base:1000,toolOut:400,outTokens:100,keepLast:0,summaryTokens:300,cacheHit:0,cacheMultiplier:.1};
            return {full:l.contextSeries(p),compact:l.contextSeries({...p,keepLast:2}),routed:l.routing({...p,shareSmall:1,escalate:true,small:{in:1,out:1,success:.6},large:{in:2,out:2,success:.9}})}}""",{})
        self.assertEqual(got['full'],[1000+500*i for i in range(10)])
        self.assertEqual(max(got['compact']),1000+300+2*500)
        self.assertAlmostEqual(got['routed']['success'],0.96)

if __name__=='__main__':unittest.main()
