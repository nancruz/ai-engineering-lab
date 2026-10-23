"""Checks for content preservation, portable links and retrieval-workbench parity."""
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
import build_course_site as site
sys.path.insert(0, str(ROOT/'tracks/rag/lab'))
from retrieval import retrieve, metrics

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.links=[];self.ids=set();self.article=[];self.depth=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.add(attrs['id'])
        if tag in ('a','link','script'):
            value=attrs.get('href') if tag!='script' else attrs.get('src')
            if value:self.links.append(value)
        if tag=='article':self.depth=1
    def handle_endtag(self,tag):
        if tag=='article':self.depth=0
    def handle_data(self,text):
        if self.depth:self.article.append(text)

class SiteChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.out=Path(cls.temp.name)/'site';site.build(cls.out)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def test_all_course_text_and_source_downloads_preserved(self):
        manifest=json.loads((self.out/'content-manifest.json').read_text())
        self.assertEqual(manifest['sessions'],144)
        self.assertEqual(len(manifest['pages']),24)
        for record in manifest['pages']:
            raw=(ROOT/record['source']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),record['sha256'])
            self.assertEqual((self.out/'sources'/record['source']).read_bytes(),raw)
            expected=Document();expected.feed('<article>'+site.render(raw.decode())+'</article>')
            actual=Document();actual.feed((self.out/record['page']).read_text())
            # URLs/layout can change, but the original article text must be byte-identical after rendering.
            self.assertEqual(''.join(expected.article),''.join(actual.article),record['source'])
    def test_relative_links_assets_and_heading_anchors_resolve(self):
        parsed={}
        for p in self.out.rglob('*.html'):
            doc=Document();doc.feed(p.read_text());parsed[p.resolve()]=doc
        for p,doc in parsed.items():
            for href in doc.links:
                url=urlsplit(href)
                if url.scheme or url.netloc:continue
                self.assertFalse(href.startswith('/'),f'Root-absolute URL breaks project Pages: {href}')
                target=(p.parent/unquote(url.path)).resolve() if url.path else p
                self.assertTrue(target.is_file(),f'{p}: {href}')
                if url.fragment and target in parsed:
                    self.assertIn(unquote(url.fragment),parsed[target].ids,f'{p}: {href}')
    def test_only_explicit_course_data_is_published(self):
        self.assertFalse(list(self.out.rglob('heldout.json')))
        self.assertFalse(list(self.out.rglob('.env')))
        self.assertFalse((self.out/'files/projects').exists())
        self.assertTrue((self.out/'files/tracks/rag/lab/data/corpus.json').is_file())
    def test_session_ids_unique_and_all_learning_weeks_present(self):
        text=(self.out/'assets/course-data.js').read_text()
        data=json.loads(text.removeprefix('window.COURSE_DATA = ').rstrip(';\n'))
        self.assertEqual(len({s['id'] for s in data['sessions']}),144)
        self.assertEqual({s['week'] for s in data['sessions']},set(range(1,53))-{13,26,39,52})
    def test_browser_retrieval_matches_actual_python_reference(self):
        docs=json.loads((ROOT/'tracks/rag/lab/data/corpus.json').read_text())
        questions=json.loads((ROOT/'tracks/rag/lab/data/dev.json').read_text())
        cases=[{'q':q,'mode':m,'k':k} for q in questions for m in ['faulty','keyword','bm25'] for k in [1,2,3,5]]
        js="""const fs=require('fs');const x=JSON.parse(fs.readFileSync(0,'utf8'));
        const learning=require('./course-site/assets/learning.js');
        process.stdout.write(JSON.stringify(x.cases.map(c=>learning.retrieve(c.q,x.docs,c.mode,c.k))));"""
        values=json.loads(subprocess.check_output(['node','-e',js],input=json.dumps({'docs':docs,'cases':cases}).encode(),cwd=ROOT))
        for case,actual in zip(cases,values):
            expected=retrieve(case['q'],docs,case['mode'],case['k'])
            self.assertEqual([x['id'] for x in actual],[x['id'] for x in expected])
            for a,b in zip(actual,expected):self.assertAlmostEqual(a['score'],b['score'],places=10)
    def test_metric_widget_matches_reference_edge_cases(self):
        cases=[(['X','A','Y'],['A','B'],3),(['A','A','B'],['A','B'],2),(['X'],[],3),(['X','Y'],['A','B'],2)]
        js="""const fs=require('fs');const l=require('./course-site/assets/learning.js');
        process.stdout.write(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8')).map(c=>l.metrics(...c))));"""
        actual=json.loads(subprocess.check_output(['node','-e',js],input=json.dumps(cases).encode(),cwd=ROOT))
        self.assertEqual(actual,[metrics(*c) for c in cases])

if __name__=='__main__':unittest.main()
