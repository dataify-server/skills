import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "skills" / "dataify-competitive-intelligence" / "scripts" / "run_research.py"
VERIFY_PATH = ROOT / "skills" / "dataify-competitive-intelligence" / "scripts" / "verify_report.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class CompetitiveIntelligenceTests(unittest.TestCase):
    def test_all_competitive_intelligence_schemas_are_valid_json(self):
        schema_dir = ROOT / "skills" / "dataify-competitive-intelligence" / "schemas"
        schemas = list(schema_dir.glob("*.schema.json"))
        self.assertGreaterEqual(len(schemas), 7)
        for schema in schemas:
            payload = json.loads(schema.read_text(encoding="utf-8"))
            self.assertEqual("https://json-schema.org/draft/2020-12/schema", payload["$schema"], schema)

    def test_dry_run_creates_bounded_plan_without_token(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER_PATH),
                    "--company", "Dataify",
                    "--competitor", "Bright Data",
                    "--module", "snapshot",
                    "--module", "pricing",
                    "--max-actions", "3",
                    "--output-dir", str(output),
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            state = json.loads((output / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(1, len(state["actions"]))
            self.assertTrue(all(action["status"] == "pending" for action in state["actions"]))
            self.assertTrue((output / "evidence-report.md").exists())

    def test_resume_does_not_resubmit_successful_actions(self):
        runner = load_module("competitive_runner", RUNNER_PATH)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_search = root / "google_search.py"
            fake_search.write_text("# test\n", encoding="utf-8")
            state_path = root / "state.json"
            state = {
                "version": 1,
                "company": "Dataify",
                "competitors": ["Bright Data"],
                "modules": ["pricing"],
                "geography": "US",
                "freshness": "12 months",
                "mode": "quick",
                "max_actions": 2,
                "actions": [
                    {"id": "a01", "entity": "Dataify", "module": "pricing", "query": "q1", "status": "success", "output": "evidence/a01.json", "error": None},
                    {"id": "a02", "entity": "Bright Data", "module": "pricing", "query": "q2", "status": "failed", "output": None, "error": "timeout"},
                ],
            }
            runner.save(state_path, state)
            args = runner.parser().parse_args(["--resume", str(root), "--autopilot"])
            with patch.object(runner, "SEARCH_SCRIPT", fake_search), patch.object(
                runner.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout='{"ok": true}\n', stderr="")
            ) as run:
                code = runner.execute(state_path, state, args)
            self.assertEqual(0, code)
            self.assertEqual(1, run.call_count)
            self.assertEqual("q2", run.call_args.args[0][-3])

    def test_retry_failed_safe_never_resets_scraper_submission(self):
        runner = load_module("competitive_safe_retry", RUNNER_PATH)
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state = {
                "actions": [
                    {"id": "a01", "type": "discover", "status": "failed", "attempts": 2, "error": "network"},
                    {"id": "a02", "type": "scrape", "status": "failed", "attempts": 1, "error": "unknown submission"},
                ]
            }
            runner.save(state_path, state)
            args = runner.parser().parse_args(["--resume", str(state_path), "--retry-failed-safe"])
            _, recovered = runner.load_or_plan(args)
            self.assertEqual("pending", recovered["actions"][0]["status"])
            self.assertEqual(0, recovered["actions"][0]["attempts"])
            self.assertEqual("failed", recovered["actions"][1]["status"])

    def test_report_verifier_accepts_grounded_structure(self):
        verifier = load_module("competitive_verifier", VERIFY_PATH)
        report = """# Report — 2026-09-03
Fact: A is documented. [Source](https://example.com/a)
Inference (medium confidence): B may follow. [Source](https://example.com/b)
## Limitations
Unknown items remain.
## Recommendations
Validate B.
"""
        self.assertEqual([], verifier.validate(report))

    def test_report_verifier_rejects_ungrounded_summary(self):
        verifier = load_module("competitive_verifier_bad", VERIFY_PATH)
        failures = verifier.validate("Competitor A is best.")
        self.assertIn("missing sources", failures)
        self.assertIn("fewer than two source URLs", failures)

    def test_source_discovery_deduplicates_and_classifies_urls(self):
        runner = load_module("competitive_routes", RUNNER_PATH)
        payload = json.dumps({
            "organic": [
                {"link": "https://www.google.com/async/folsrch?q=Acme"},
                {"link": "https://acme.example/pricing?utm_source=test"},
                {"link": "https://acme.example/pricing"},
                {"link": "https://github.com/acme/repo"},
                {"link": "https://www.amazon.com/acme/dp/B000000000"},
            ]
        })
        urls = runner.extract_urls(payload)
        self.assertEqual(4, len(urls))
        ranked = runner.rank_urls(urls, {"entity": "Acme", "module": "pricing"})
        self.assertNotIn("google.com/async", " ".join(ranked))
        self.assertEqual("https://acme.example/pricing", ranked[0])
        self.assertEqual(("fetch", "dataify-web-unlocker", None), runner.classify_url(ranked[0]))
        self.assertTrue(any(runner.classify_url(url)[1] == "scraper-github-repository-by-repo-url" for url in ranked))
        self.assertTrue(any(runner.classify_url(url)[1] == "scraper-amazon-comment" for url in ranked))

        state = {"max_actions": 4, "actions": [{"id": "a01", "entity": "Acme", "module": "pricing"}]}
        runner.expand_discovered_actions(state, state["actions"][0], payload)
        self.assertEqual(4, len(state["actions"]))
        self.assertEqual("fetch", state["actions"][1]["type"])

    def test_github_builder_route_uses_required_repo_url_parameter(self):
        runner = load_module("competitive_github_command", RUNNER_PATH)
        command = runner.command_for({
            "type": "scrape",
            "capability": "scraper-github-repository-by-repo-url",
            "tool_sign": "github_repository_by-repo-url",
            "url": "https://github.com/dataify-server/skills",
        })
        payload = json.loads(command[command.index("--params-json") + 1])
        self.assertEqual({"repo_url": "https://github.com/dataify-server/skills"}, payload)

    def test_structured_report_rejects_dangling_evidence(self):
        verifier = load_module("competitive_verifier_links", VERIFY_PATH)
        report = {
            "research_date": "2026-09-03",
            "evidence": [{
                "evidence_id": "ev-1",
                "source": {"url": "https://example.com", "query": None},
                "content": {"raw_path": "evidence/a.json", "sha256": "abc"},
            }],
            "findings": [{"finding_id": "f-1", "evidence_ids": ["ev-missing"], "confidence": "high"}],
            "status": "complete",
        }
        failures = verifier.validate_structured(report)
        self.assertTrue(any("dangling evidence" in item for item in failures))

    def test_structured_report_rejects_evidence_only_draft(self):
        verifier = load_module("competitive_verifier_draft", VERIFY_PATH)
        failures = verifier.validate_structured({"research_date": "2026-09-03", "evidence": [], "findings": [], "status": "evidence_ready_analysis_required"})
        self.assertIn("report analysis is not complete", failures)

    def test_snapshot_comparison_detects_content_change(self):
        outputs_path = RUNNER_PATH.with_name("research_outputs.py")
        outputs = load_module("competitive_outputs", outputs_path)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "old.json"
            new = root / "new.json"
            base = {"action_id": "a01", "content": {"sha256": "old"}}
            old.write_text(json.dumps([base]), encoding="utf-8")
            changed = {"action_id": "a01", "content": {"sha256": "new"}}
            new.write_text(json.dumps([changed]), encoding="utf-8")
            result = outputs.compare(old, new)
            self.assertEqual("content_changed", result[0]["change_type"])

    def test_monitor_refresh_resets_attempt_budget(self):
        monitor_path = RUNNER_PATH.with_name("monitor_research.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline = root / "baseline"
            baseline.mkdir()
            state = {
                "version": 1, "company": "Acme", "competitors": ["Rival"], "modules": ["pricing"],
                "max_actions": 1, "geography": "US", "freshness": "12 months", "mode": "quick",
                "actions": [{"id": "a01", "entity": "Acme", "module": "pricing", "type": "discover", "capability": "dataify-google-search", "query": "q", "depends_on": [], "status": "success", "output": "old.json", "error": None, "attempts": 2}],
            }
            (baseline / "state.json").write_text(json.dumps(state), encoding="utf-8")
            output = root / "monitor"
            result = subprocess.run([sys.executable, str(monitor_path), "--baseline", str(baseline), "--output-root", str(output), "--dry-run"], capture_output=True, text=True, check=False)
            self.assertEqual(0, result.returncode, result.stderr)
            refreshed = json.loads(next(output.glob("*/state.json")).read_text(encoding="utf-8"))
            self.assertEqual(0, refreshed["actions"][0]["attempts"])

    def test_discovery_to_fetch_to_evidence_end_to_end(self):
        runner = load_module("competitive_e2e", RUNNER_PATH)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            search = root / "search.py"
            unlocker = root / "unlocker.py"
            search.write_text("# test\n", encoding="utf-8")
            unlocker.write_text("# test\n", encoding="utf-8")
            args = runner.parser().parse_args([
                "--company", "Acme", "--company-domain", "acme.example", "--competitor", "Rival", "--module", "pricing",
                "--max-actions", "2", "--output-dir", str(root / "run"), "--autopilot",
            ])
            state_path, state = runner.load_or_plan(args)

            def fake_run(command, **kwargs):
                if "--q" in command:
                    return subprocess.CompletedProcess(command, 0, stdout='{"organic":[{"link":"https://acme.example/pricing"}]}', stderr="")
                return subprocess.CompletedProcess(command, 0, stdout="Official pricing page", stderr="")

            with patch.object(runner, "SEARCH_SCRIPT", search), patch.object(runner, "UNLOCKER_SCRIPT", unlocker), patch.object(runner.subprocess, "run", side_effect=fake_run):
                code = runner.execute(state_path, state, args)
            self.assertEqual(0, code)
            final_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(["discover", "fetch"], [item["type"] for item in final_state["actions"]])
            evidence = json.loads((state_path.parent / "evidence.json").read_text(encoding="utf-8"))
            self.assertEqual("first_party", evidence[1]["source"]["source_type"])
            self.assertTrue((state_path.parent / "report.json").exists())

    def test_findings_build_a_complete_verifiable_report(self):
        outputs = load_module("competitive_complete_report", RUNNER_PATH.with_name("research_outputs.py"))
        verifier = load_module("competitive_complete_verify", VERIFY_PATH)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "raw.txt").write_text("Official evidence", encoding="utf-8")
            state = {
                "company": "Acme", "competitors": ["Rival"], "decision": "Choose", "audience": "Team",
                "modules": ["product"], "geography": "US", "freshness": "12 months", "mode": "quick",
                "actions": [{"id": "a01", "entity": "Acme", "module": "product", "type": "fetch", "status": "success", "url": "https://acme.example/docs", "output": "raw.txt"}],
            }
            state_path = root / "state.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            evidence = outputs.normalize(state_path)
            self.assertEqual("external_page", evidence[0]["source"]["source_type"])
            findings = [{
                "finding_id": "f-1", "title": "Documented capability", "type": "product_gap",
                "fact": "The capability is documented.", "inference": "It may reduce integration effort.",
                "recommendation": "Validate it with a workload test.", "confidence": "medium",
                "evidence_ids": [evidence[0]["evidence_id"]], "priority": "P1",
            }]
            findings_path = root / "findings.json"
            findings_path.write_text(json.dumps(findings), encoding="utf-8")
            _, report_json = outputs.build_report(state_path, findings_path)
            report = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["status"])
            self.assertEqual([], verifier.validate_structured(report))


if __name__ == "__main__":
    unittest.main()
