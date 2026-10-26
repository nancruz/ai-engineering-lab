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
        self.assertEqual(len(pages),28)
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
        self.assertEqual(courses,['rag'])
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

if __name__=='__main__':unittest.main()
