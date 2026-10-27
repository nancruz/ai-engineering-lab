"""Optional standard-library checks for the directly editable static HTML course."""
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import unittest
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'docs'
RAG=DOCS/'rag'
sys.path.insert(0,str(ROOT/'tracks/rag/lab'))
from retrieval import retrieve,metrics

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.add(attrs['id'])
        value=attrs.get('src') if tag=='script' else attrs.get('href') if tag in ('a','link') else None
        if value:self.links.append(value)

def course_data():
    value=(RAG/'assets/course-data.js').read_text().split('window.COURSE_DATA = ',1)[1]
    return json.loads(value.rstrip(';\n'))

class StaticCourseChecks(unittest.TestCase):
    def test_html_links_and_assets_resolve_without_source_files(self):
        pages={}
        for path in DOCS.rglob('*.html'):
            page=Page();page.feed(path.read_text());pages[path.resolve()]=page
        self.assertEqual(len(pages),47)
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
        self.assertFalse(list(DOCS.rglob('heldout.json')))
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
    def test_navigation_has_sessions_not_a_duplicate_content_index(self):
        data=course_data()
        self.assertEqual(len({s['id'] for s in data['sessions']}),144)
        self.assertEqual({s['week'] for s in data['sessions']},set(range(1,53))-{13,26,39,52})
        self.assertTrue(all('text' not in page for page in data['search']))
    def test_retrieval_and_metric_widgets_still_match_the_lab(self):
        data=course_data()
        cases=[{'q':q,'mode':m,'k':k} for q in data['questions'] for m in ['faulty','keyword','bm25'] for k in [1,2,3,5]]
        js="""const fs=require('fs'),l=require('./docs/rag/assets/learning.js'),x=JSON.parse(fs.readFileSync(0,'utf8'));
        process.stdout.write(JSON.stringify(x.cases.map(c=>l.retrieve(c.q,x.docs,c.mode,c.k))));"""
        results=json.loads(subprocess.check_output(['node','-e',js],input=json.dumps({'cases':cases,'docs':data['corpus']}).encode(),cwd=ROOT))
        for case,result in zip(cases,results):
            expected=retrieve(case['q'],data['corpus'],case['mode'],case['k'])
            self.assertEqual([x['id'] for x in result],[x['id'] for x in expected])
            for a,b in zip(result,expected):self.assertAlmostEqual(a['score'],b['score'],places=10)
        example=metrics(['X','A','Y'],['A','B'],3)
        js="process.stdout.write(JSON.stringify(require('./docs/rag/assets/learning.js').metrics(['X','A','Y'],['A','B'],3)))"
        self.assertEqual(json.loads(subprocess.check_output(['node','-e',js],cwd=ROOT)),example)

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
        self.assertEqual(data['corpus'],json.loads((ROOT/'tracks/rag/lab/data/corpus.json').read_text()))
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
