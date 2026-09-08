import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class NaturalLanguageIssueRegressions(unittest.TestCase):
    def test_amazon_keyword_search_defaults_to_us_domain(self):
        product_list = load_module(
            "amazon_product_list",
            ROOT / "skills/scraper-amazon-product-list/scripts/submit_amazon_product_list.py",
        )
        args = argparse.Namespace(
            keyword="wireless mouse", domain=None, page_turning=1,
            file_name="{{TasksID}}", no_wait=True, wait_timeout=600,
        )
        with patch.dict(os.environ, {"DATAIFY_API_TOKEN": "test"}), \
             patch.object(product_list, "submit_builder", return_value="task_123") as submit, \
             patch.object(sys, "argv", ["submit", "--keyword", args.keyword, "--no-wait"]):
            self.assertEqual(0, product_list.main())
        self.assertEqual(product_list.DEFAULT_DOMAIN, submit.call_args.args[2])

        global_product = load_module(
            "amazon_global_product",
            ROOT / "skills/scraper-amazon-global-product/scripts/submit_amazon_global_product.py",
        )
        parsed = global_product.build_parser().parse_args(["keyword", "--keyword", "wireless mouse"])
        _builder, _spider, rows, _file, summary = parsed.handler(parsed)
        self.assertEqual(global_product.DEFAULT_DOMAIN, rows[0]["domain"])
        self.assertEqual(global_product.DEFAULT_DOMAIN, summary["domain"])

    def test_amazon_business_error_payload_does_not_crash(self):
        module = load_module(
            "amazon_product_list_error",
            ROOT / "skills/scraper-amazon-product-list/scripts/submit_amazon_product_list.py",
        )

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self):
                return b'{"code":520,"data":"Other Errors"}'

        with patch("urllib.request.urlopen", return_value=Response()):
            with self.assertRaisesRegex(RuntimeError, "did not return task_id"):
                module.submit_builder("test", "mouse", module.DEFAULT_DOMAIN, 1, "{{TasksID}}")

    def test_invalid_unlocker_url_is_rejected_before_network(self):
        module = load_module(
            "web_unlocker",
            ROOT / "skills/dataify-web-unlocker/scripts/invoke-dataify-web-unlocker.py",
        )
        with patch.object(sys, "argv", ["unlock", "--url", "not-a-valid-url"]), \
             patch("urllib.request.urlopen") as request:
            with self.assertRaises(SystemExit) as raised:
                module.main()
        self.assertEqual(2, raised.exception.code)
        request.assert_not_called()

    def test_catalog_targets_are_required_and_urls_are_validated(self):
        runtime = ROOT / "skills/dataify-task-operations/scripts"
        sys.path.insert(0, str(runtime))
        try:
            module = load_module("catalog_builder_regression", runtime / "catalog_builder.py")
        finally:
            sys.path.remove(str(runtime))
        catalog = module.load_catalog(
            ROOT / "skills/scraper-airbnb-product-by-searchurl/scripts"
        )
        tool = module.find_tool(catalog, "airbnb_product_by-searchurl")
        with self.assertRaisesRegex(ValueError, "missing required values: searchurl"):
            module.validate_required(tool, [{}])
        with self.assertRaisesRegex(ValueError, "starting with https://"):
            module.validate_required(tool, [{"searchurl": "not-a-valid-url"}])

        tiktok = module.load_catalog(
            ROOT / "skills/scraper-tiktok-comment-by-url/scripts"
        )
        comments = module.find_tool(tiktok, "tiktok_comment_by-url")
        with self.assertRaisesRegex(ValueError, "missing required values: url"):
            module.validate_required(comments, [{}])

    def test_google_news_relative_links_are_completed_recursively(self):
        module = load_module(
            "google_news_regression",
            ROOT / "skills/serp-google-news/scripts/google_news.py",
        )
        payload = {"news": [{"title": "AI", "link": "/goto?url=abc"}]}
        normalized = json.loads(module.normalize_response_body(json.dumps(payload).encode()))
        self.assertEqual(
            "https://news.google.com/goto?url=abc",
            normalized["news"][0]["link"],
        )

    def test_release_keeps_catalog_references(self):
        build = load_module("build_release_regression", ROOT / "scripts/build_release.py")
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "release"
            build.build(output)
            catalogs = sorted(ROOT.glob("skills/*/references/tool-params.json"))
            self.assertEqual(8, len(catalogs))
            for source in catalogs:
                catalog = output / source.parent.parent.name / "references/tool-params.json"
                self.assertTrue(catalog.is_file(), catalog)
                self.assertTrue(json.loads(catalog.read_text(encoding="utf-8")))

    def test_catalog_references_are_not_gitignored(self):
        catalogs = sorted(ROOT.glob("skills/*/references/tool-params.json"))
        self.assertEqual(8, len(catalogs))
        completed = subprocess.run(
            ["git", "check-ignore", *[str(path) for path in catalogs]],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual("", completed.stdout, completed.stdout)

    def test_all_python_entrypoints_configure_utf8_stdio(self):
        missing = []
        for script in ROOT.glob("skills/*/scripts/*.py"):
            text = script.read_text(encoding="utf-8")
            if 'if __name__ == "__main__"' in text or "if __name__ == '__main__'" in text:
                if 'reconfigure(encoding="utf-8"' not in text:
                    missing.append(str(script.relative_to(ROOT)))
        self.assertEqual([], missing)

    def test_chinese_error_is_utf8_even_when_parent_encoding_is_legacy(self):
        script = ROOT / "skills/serp-google-news/scripts/google_news.py"
        env = dict(os.environ)
        env.pop("DATAIFY_API_TOKEN", None)
        env["PYTHONIOENCODING"] = "cp1252"
        completed = subprocess.run(
            [sys.executable, str(script), "--q", "测试"],
            env=env,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(2, completed.returncode)
        output = (completed.stdout + completed.stderr).decode("utf-8")
        self.assertIn("缺少", output)


if __name__ == "__main__":
    unittest.main()
