import contextlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(path.parent))


class AIWebSkillTests(unittest.TestCase):
    def test_fixed_unique_ids(self):
        search = load('ai_web_search_test', ROOT / 'skills/ai-web-search/scripts/search.py')
        map_module = load('ai_web_map_test', ROOT / 'skills/ai-web-map/scripts/map.py')
        extract = load('ai_web_extract_test', ROOT / 'skills/ai-web-extract/scripts/extract.py')
        self.assertEqual('search_web', search.MODES['web']['unique_id'])
        self.assertEqual('search_shopping', search.MODES['shopping']['unique_id'])
        self.assertEqual('search_news', search.MODES['news']['unique_id'])
        self.assertEqual('search_scholar', search.MODES['scholar']['unique_id'])
        self.assertEqual('map', map_module.UNIQUE_ID)
        self.assertEqual('extract', extract.UNIQUE_ID)

    def test_time_range_is_limited_to_web_and_news(self):
        search = load('ai_web_search_time_range_test', ROOT / 'skills/ai-web-search/scripts/search.py')
        for mode in ('web', 'news'):
            args = search.build_parser().parse_args([mode, '--query', 'test', '--time-range', 'week'])
            self.assertEqual('week', args.time_range)
        for mode in ('shopping', 'scholar'):
            args = search.build_parser().parse_args([mode, '--query', 'test'])
            self.assertFalse(hasattr(args, 'time_range'))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            search.build_parser().parse_args(['shopping', '--query', 'test', '--time-range', 'week'])

    def test_web_mode_uses_search_web_and_uppercase_country(self):
        search = load('ai_web_search_web_mode_test', ROOT / 'skills/ai-web-search/scripts/search.py')
        args = search.build_parser().parse_args(['web', '--query', 'AI news', '--country', 'us', '--time-range', 'week'])
        payload = search.build_payload(args)
        self.assertEqual('search_web', payload['unique_id'])
        self.assertEqual('web', payload['source'])
        self.assertEqual('US', payload['country'])
        self.assertEqual('week', payload['time_range'])

    def test_default_base_url_uses_production_domain(self):
        search = load('ai_web_search_base_url_test', ROOT / 'skills/ai-web-search/scripts/search.py')
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual('https://aiwebapi.dataify.com', search.resolve_base_url(None))

    def test_extract_formats_are_an_array(self):
        extract = load('ai_web_extract_formats_test', ROOT / 'skills/ai-web-extract/scripts/extract.py')
        args = extract.build_parser().parse_args(['--url', 'https://example.com', '--format', 'markdown', '--format', 'links'])
        payload = extract.build_payload(args)
        self.assertEqual(['markdown', 'links'], payload['formats'])

    def test_request_source_is_skills_for_all_ai_web_tools(self):
        search = load('ai_web_search_request_source_test', ROOT / 'skills/ai-web-search/scripts/search.py')
        extract = load('ai_web_extract_request_source_test', ROOT / 'skills/ai-web-extract/scripts/extract.py')
        map_module = load('ai_web_map_request_source_test', ROOT / 'skills/ai-web-map/scripts/map.py')

        search_args = search.build_parser().parse_args(['web', '--query', 'AI news'])
        extract_args = extract.build_parser().parse_args(['--url', 'https://example.com'])
        map_args = map_module.build_parser().parse_args(['--url', 'https://example.com'])

        self.assertEqual('skills', search.build_payload(search_args)['request_source'])
        self.assertEqual('skills', extract.build_payload(extract_args)['request_source'])
        self.assertEqual('skills', map_module.build_payload(map_args)['request_source'])


if __name__ == '__main__':
    unittest.main()
