import importlib.util
from pathlib import Path
import unittest
import tempfile
import subprocess
import sys
import json
import argparse
import io
import contextlib
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def load(skill, script):
    spec = importlib.util.spec_from_file_location(skill, ROOT / 'skills' / skill / 'scripts' / script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class AuditRegressions(unittest.TestCase):
    def test_research_intent_and_urls(self):
        m = load('dataify-live-research', 'run_research.py')
        self.assertNotEqual(m.build_plan('Dataify pricing changes','US','7 days',3), m.build_plan('Dataify security incidents','US','7 days',3))
        self.assertNotEqual(m.normalize_source_url('https://x.org/?id=1'),m.normalize_source_url('https://x.org/?id=2'))
        rows = [{'source':'https://x.org/'+str(i),'content':'Water resources management. '*30} for i in range(2)]
        self.assertFalse(m.quality_gate_sources(rows,'研究阿里云最近七天的产品变化')[0])

    def test_mcp_rejects_protocol_error(self):
        m=load('dataify-mcp','configure_mcp.py')
        class Response:
            status=200
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self,*args): return b'{"jsonrpc":"2.0","id":1,"error":{"code":-32601}}'
        with patch.object(m.urllib.request,'urlopen',return_value=Response()):
            self.assertNotEqual('ready',m.verify_server('https://example.org')['status'])
        self.assertEqual('config.toml',m.target_for('codex').name)

    def test_builder_routes_by_host_and_page(self):
        m=load('dataify-scraper-builder','build_scraper.py')
        self.assertIsNone(m.prebuilt_for('https://example.org/?ref=amazon.com'))
        self.assertIsNone(m.prebuilt_for('https://linkedin.com/in/person'))

    def test_packaged_workflows_are_self_contained(self):
        spec=importlib.util.spec_from_file_location('release',ROOT/'scripts/build_release.py')
        release=importlib.util.module_from_spec(spec); spec.loader.exec_module(release)
        with tempfile.TemporaryDirectory() as temp:
            release.build(Path(temp)/'release')
            for name,script in [('price','run_price_intelligence.py'),('review','run_review_intelligence.py'),('lead','run_lead_intelligence.py'),('brand','run_brand_monitoring.py')]:
                skill='dataify-brand-monitoring' if name=='brand' else 'dataify-'+name+'-intelligence'
                result=subprocess.run([sys.executable,str(Path(temp)/'release'/skill/'scripts'/script),'--help'],capture_output=True,text=True)
                self.assertEqual(0,result.returncode,result.stderr)

    def test_codex_toml_preserves_other_servers(self):
        m=load('dataify-mcp','configure_mcp.py')
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'config.toml'
            path.write_text('[mcp_servers.other]\nurl="https://other.org"\n')
            m.configure(path,'fake',['user_info'],write=True)
            value=m.tomllib.loads(path.read_text())
            self.assertIn('other',value['mcp_servers'])
            self.assertIn('dataify',value['mcp_servers'])

    def test_seo_partial_and_robot_groups(self):
        m=load('dataify-seo-audit','run_seo_audit.py')
        def fetch(url,*args,**kwargs):
            body='<title>Public page documentation</title><h1>Content</h1>'
            if url.endswith('robots.txt'):
                body='User-agent: *\nAllow: /\n\nUser-agent: BadBot\nDisallow: /\n'
            if url.endswith('sitemap.xml'):
                body='<urlset><url><loc>https://example.org/broken</loc></url></urlset>'
            if url.endswith('broken'):
                return {'ok':False,'status':503,'body':'','error':{'message':'failed'}}
            return {'ok':True,'status':200,'body':body,'error':None}
        with tempfile.TemporaryDirectory() as temp:
            args=argparse.Namespace(url='https://example.org/',max_pages=2,output_dir=Path(temp),geography='us',keywords='',dry_run=False)
            with patch.object(m,'token_from_environment',return_value='fake'),patch.object(m,'unlock',side_effect=fetch),patch.object(m,'search',return_value={'ok':False,'status':503,'body':'','error':{'message':'failed'}}),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(2,m.run(args))
            report=json.loads((Path(temp)/'report.json').read_text())
            self.assertEqual('partial',report['status'])
            self.assertFalse(report['site_findings'])
            self.assertIn('failed',(Path(temp)/'report.md').read_text())

    def test_builder_submission_not_repeated_on_resume(self):
        m=load('dataify-task-operations','business_workflow.py')
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'state.json'
            path.write_text(json.dumps({'kind':'review','subject':'test','actions':[{'id':'a01','type':'url','capability':'scraper-amazon-comment','stage':'detail','subject':'test','status':'failed','attempts':1,'error':'submission timeout','output':None,'url':'https://www.amazon.com/dp/test'}]}))
            with patch.dict(m.os.environ,{'DATAIFY_API_TOKEN':'fake'}),patch.object(m,'execute_action') as call,patch.object(m,'build_outputs',return_value={'status':'failed','metrics':{'record_count':0}}),contextlib.redirect_stdout(io.StringIO()):
                m.run('review',['--resume',str(path)])
            call.assert_not_called()
