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
RUNTIME_PATH = ROOT / "skills/dataify-task-operations/scripts/business_workflow.py"


def load_runtime():
    spec = importlib.util.spec_from_file_location("business_workflow_test", RUNTIME_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BusinessIntelligenceTests(unittest.TestCase):
    def test_four_skill_entrypoints_exist_and_help(self):
        cases = {
            "price": "run_price_intelligence.py",
            "review": "run_review_intelligence.py",
            "lead": "run_lead_intelligence.py",
            "brand": "run_brand_monitoring.py",
        }
        for name, script in cases.items():
            path = ROOT / "skills" / "dataify-{}-intelligence".format(name) / "scripts" / script
            if name == "brand":
                path = ROOT / "skills/dataify-brand-monitoring/scripts" / script
            result = subprocess.run([sys.executable, str(path), "--help"], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_plans_are_bounded_and_domain_specific(self):
        runtime = load_runtime()
        cases = (("price", "Headphones", "dataify-google-shopping"), ("review", "App", "dataify-google-search"),
                 ("lead", "AI startups", "dataify-google-search"), ("brand", "Dataify", "dataify-google-news"))
        for kind, subject, capability in cases:
            args = runtime.parser(kind).parse_args([runtime.CONFIG[kind]["input_flag"], subject, "--max-actions", "1"])
            actions = runtime.make_actions(kind, subject, args)[:1]
            self.assertEqual(1, len(actions))
            self.assertEqual(capability, actions[0]["capability"])

    def test_dry_run_needs_no_token_and_writes_state(self):
        script = ROOT / "skills/dataify-price-intelligence/scripts/run_price_intelligence.py"
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            result = subprocess.run([sys.executable, str(script), "--product", "Camera", "--max-actions", "1",
                                     "--output-dir", directory, "--dry-run"], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((Path(directory) / "state.json").exists())
            self.assertEqual(1, len(json.loads(result.stdout)["actions"]))

    def test_missing_token_fails_without_exposing_a_value(self):
        script = ROOT / "skills/dataify-brand-monitoring/scripts/run_brand_monitoring.py"
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            result = subprocess.run([sys.executable, str(script), "--brand", "Acme", "--output-dir", directory],
                                    capture_output=True, text=True)
            self.assertEqual(1, result.returncode)
            self.assertIn("DATAIFY_API_TOKEN is not configured", result.stderr)

    def test_success_creates_raw_evidence_hash_and_report(self):
        runtime = load_runtime()
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"DATAIFY_API_TOKEN": "secret"}):
            with patch.object(runtime, "execute_action", return_value=subprocess.CompletedProcess([], 0, stdout=json.dumps({
                "shopping_results": [{"title": "Camera", "price": "$99", "link": "https://shop.example/camera"}]
            }), stderr="")):
                code = runtime.run("price", ["--product", "Camera", "--max-actions", "1", "--output-dir", directory])
            self.assertEqual(2, code)
            report = json.loads((Path(directory) / "report.json").read_text())
            self.assertEqual("insufficient_evidence", report["status"])
            self.assertEqual(1, report["metrics"]["record_count"])
            self.assertEqual(99.0, report["metrics"]["minimum_price"])
            self.assertEqual(64, len(report["evidence"][0]["sha256"]))

    def test_resume_skips_successful_action(self):
        runtime = load_runtime()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "raw").mkdir()
            (root / "raw/a01.json").write_text('{"organic":[]}', encoding="utf-8")
            state = {"version": 1, "kind": "lead", "subject": "AI", "updated_at": runtime.now(),
                     "actions": [{"id": "a01", "type": "search", "capability": "dataify-google-search", "query": "AI",
                                  "url": None, "subject": "AI", "status": "success", "attempts": 1,
                                  "output": "raw/a01.json", "error": None}]}
            runtime.write_json(root / "state.json", state)
            with patch.dict(os.environ, {"DATAIFY_API_TOKEN": "secret"}), patch.object(runtime, "execute_action") as call:
                self.assertEqual(2, runtime.run("lead", ["--resume", str(root)]))
            call.assert_not_called()

    def test_review_known_amazon_url_uses_structured_scraper(self):
        runtime = load_runtime()
        action = runtime.url_action("a01", "https://www.amazon.com/dp/B000000000", "Product", "review")
        self.assertEqual("scraper-amazon-comment", action["capability"])
        self.assertIn("submit_amazon_comment.py", " ".join(runtime.command(action)))

    def test_explicit_source_is_prioritized_inside_action_budget(self):
        runtime = load_runtime()
        args = runtime.parser("review").parse_args([
            "--subject", "Product", "--source-url", "https://www.amazon.com/dp/B000000000", "--max-actions", "1"
        ])
        actions = runtime.make_actions("review", args.subject, args)[:1]
        self.assertEqual("scraper-amazon-comment", actions[0]["capability"])

    def test_concatenated_builder_progress_and_result_uses_final_json(self):
        runtime = load_runtime()
        text = '{"task_id":"abc12345","status":"submitted"}\n' + json.dumps({
            "ok": True,
            "task_id": "abc12345",
            "status": "succeeded",
            "data": [{"review": "Great sound", "rating": 5}],
        })
        payload = runtime.decode_json_stream(text)
        self.assertTrue(payload["ok"])
        records = runtime.records_for("review", payload, "ev-1")
        self.assertEqual("Great sound", records[0]["text"])

    def test_price_ranges_are_separated_by_currency(self):
        runtime = load_runtime()
        metrics = runtime.analyze("price", [
            {"price": "$100", "currency": "$"}, {"price": "RM 100", "currency": "RM"}
        ])
        self.assertNotIn("minimum_price", metrics)
        self.assertEqual({"$", "RM"}, set(metrics["observed_price_ranges_by_currency"]))

    def test_price_metrics_exclude_noncomparable_accessories(self):
        runtime = load_runtime()
        metrics = runtime.analyze("price", [
            {"price": "$20", "currency": "$", "comparable": False},
            {"price": "$200", "currency": "$", "comparable": True},
        ])
        self.assertEqual(200.0, metrics["minimum_price"])

    def test_leads_require_company_entity_urls(self):
        runtime = load_runtime()
        payload = {"organic": [
            {"title": "Job", "link": "https://linkedin.com/jobs/view/1"},
            {"title": "Acme", "link": "https://linkedin.com/company/acme"},
        ]}
        records = runtime.records_for("lead", payload, "ev-1", "AI companies")
        self.assertEqual(["Acme"], [row["company"] for row in records])
        self.assertIn("qualification_score", records[0])

    def test_brand_filter_removes_similar_names(self):
        runtime = load_runtime()
        payload = {"organic": [
            {"title": "Dataify launches", "link": "https://news.example/dataify"},
            {"title": "Digify launches", "link": "https://news.example/digify"},
        ]}
        records = runtime.records_for("brand", payload, "ev-1", "Dataify")
        self.assertEqual(["Dataify launches"], [row["title"] for row in records])

    def test_atomic_script_output_is_decoded_as_utf8(self):
        runtime = load_runtime()
        action = {"type": "search", "capability": "dataify-google-search", "query": "中文", "geography": "cn"}
        with patch.object(runtime, "command", return_value=[sys.executable, __file__]), patch.object(
            runtime.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout="中文", stderr="")
        ) as run:
            runtime.execute_action(action, "secret")
        self.assertEqual("utf-8", run.call_args.kwargs["encoding"])
        self.assertEqual("replace", run.call_args.kwargs["errors"])

    def test_serp_parser_ignores_related_and_navigation_records(self):
        runtime = load_runtime()
        payload = {
            "organic": [{"title": "Notion review", "link": "https://reviews.example/notion", "description": "Great app"}],
            "related": [{"text": "Notion login", "link": "https://google.com/search?q=notion+login"}],
            "navigation": [{"title": "Images", "href": "https://google.com/images"}],
        }
        records = runtime.records_for("review", payload, "ev-1", "Notion")
        self.assertEqual(["https://reviews.example/notion"], [row["url"] for row in records])

    def test_freshness_filter_excludes_old_dated_records(self):
        runtime = load_runtime()
        records = [
            {"text": "old", "date": "2021-03-18", "url": "https://example/old"},
            {"text": "new", "date": "2026-08-20", "url": "https://example/new"},
        ]
        kept, excluded = runtime.apply_scope_filters("review", records, "6 months", "US", as_of="2026-09-04T00:00:00+00:00")
        self.assertEqual(["new"], [row["text"] for row in kept])
        self.assertEqual(1, excluded["outside_freshness"])

    def test_geography_filter_excludes_explicit_lead_mismatch(self):
        runtime = load_runtime()
        records = [
            {"company": "US Co", "location": "New York, United States"},
            {"company": "ZA Co", "location": "Cape Town, South Africa"},
        ]
        kept, excluded = runtime.apply_scope_filters("lead", records, "", "US")
        self.assertEqual(["US Co"], [row["company"] for row in kept])
        self.assertEqual(1, excluded["geography_mismatch"])

    def test_acceptance_gate_rejects_empty_brand_report(self):
        runtime = load_runtime()
        gate = runtime.acceptance_gate("brand", [], {"record_count": 0})
        self.assertFalse(gate["accepted"])
        self.assertIn("external mention", gate["reasons"][0])

    def test_acceptance_gate_requires_two_comparable_prices(self):
        runtime = load_runtime()
        one = [{"title": "Camera", "price": "$99", "currency": "$", "comparable": True, "url": "https://a"}]
        gate = runtime.acceptance_gate("price", one, runtime.analyze("price", one))
        self.assertFalse(gate["accepted"])

    def test_acceptance_gate_requires_detail_evidence_for_review(self):
        runtime = load_runtime()
        records = [{"text": "Great app", "url": "https://example/review", "evidence_stage": "discovery"}] * 3
        self.assertFalse(runtime.acceptance_gate("review", records, runtime.analyze("review", records))["accepted"])

    def test_application_error_payload_is_not_success(self):
        runtime = load_runtime()
        ok, error = runtime.validate_action_result(subprocess.CompletedProcess([], 0, stdout='{"code":520,"data":"Other Errors"}', stderr=""))
        self.assertFalse(ok)
        self.assertIn("520", error)

    def test_detail_actions_are_added_from_discovery_within_budget(self):
        runtime = load_runtime()
        state = {"kind": "review", "subject": "Notion", "max_actions": 3, "actions": [
            {"id": "a01", "type": "search", "capability": "dataify-google-search", "query": "Notion reviews",
             "url": None, "subject": "Notion", "status": "success", "attempts": 1, "output": "raw/a01.json", "error": None, "geography": "US"}
        ]}
        payloads = {"a01": {"organic": [
            {"title": "Notion reviews", "link": "https://www.trustpilot.com/review/notion.so"},
            {"title": "Notion reviews", "link": "https://www.capterra.com/p/186596/Notion/reviews/"},
        ]}}
        added = runtime.add_detail_actions(state, payloads)
        self.assertEqual(2, added)
        self.assertTrue(all(action["stage"] == "detail" for action in state["actions"][1:]))

    def test_lead_scoring_does_not_call_keyword_overlap_high_fit(self):
        runtime = load_runtime()
        payload = {"organic": [{
            "title": "Generic AI Company", "link": "https://linkedin.com/company/generic-ai",
            "description": "AI startup data engineers web data"
        }]}
        records = runtime.records_for("lead", payload, "ev-1", "AI startups hiring data engineers web data")
        self.assertLess(records[0]["qualification_score"], 70)
        self.assertIn("requires_detail_verification", records[0]["missing_fields"])

    def test_copied_business_workflow_files_are_not_shipped(self):
        for folder in ("dataify-brand-monitoring", "dataify-lead-intelligence", "dataify-price-intelligence", "dataify-review-intelligence"):
            self.assertFalse((ROOT / "skills" / folder / "scripts" / "business_workflow.py").exists())


if __name__ == "__main__":
    unittest.main()
