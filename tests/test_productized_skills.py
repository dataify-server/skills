import importlib.util
import json
import os
from pathlib import Path
import py_compile
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "dataify-agent-onboarding", "dataify-mcp", "dataify-live-research",
    "dataify-seo-audit", "dataify-scraper-builder", "dataify-api-best-practices",
)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class ProductizedSkillTests(unittest.TestCase):
    def test_all_six_skills_have_release_metadata(self):
        for name in SKILLS:
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("version:", text, name)
            self.assertIn("author:", text, name)
            self.assertIn("documentation:", text, name)
    def test_all_six_skills_have_publishable_surface(self):
        for name in SKILLS:
            folder = ROOT / "skills" / name
            text = (folder / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: {}".format(name), text)
            self.assertIn("## Quick Start", text)
            self.assertTrue((folder / "agents" / "openai.yaml").is_file())
            self.assertTrue(list((folder / "scripts").glob("*.py")), name)

    def test_onboarding_detects_platform_and_never_returns_token(self):
        module = load("onboarding_test", ROOT / "skills/dataify-agent-onboarding/scripts/onboard.py")
        result = module.assess("research competitors", system="Windows", shell="powershell.exe", environ={"DATAIFY_API_TOKEN": "super-secret"})
        self.assertEqual("configured", result["credential_status"])
        self.assertEqual("powershell", result["environment"]["shell"])
        self.assertEqual("live-research", result["recommended_path"])
        self.assertNotIn("super-secret", json.dumps(result))

    def test_mcp_config_merges_without_destroying_other_servers(self):
        module = load("mcp_config_test", ROOT / "skills/dataify-mcp/scripts/configure_mcp.py")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "mcp.json"
            target.write_text(json.dumps({"mcpServers": {"other": {"url": "https://example.com"}}}), encoding="utf-8")
            result = module.configure(target, "secret value", ["user_info", "web_unlocker"], write=True)
            payload = json.loads(target.read_text(encoding="utf-8"))
            self.assertIn("other", payload["mcpServers"])
            self.assertIn("dataify", payload["mcpServers"])
            self.assertTrue(result["backup"])
            self.assertNotIn("secret value", json.dumps(result))

    def test_live_research_plan_is_bounded_and_diverse(self):
        module = load("live_research_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        plan = module.build_plan("AI agent web data market", "US", "12 months", 4)
        self.assertEqual(4, len(plan))
        self.assertEqual(4, len({item["query"] for item in plan}))
        self.assertTrue(all(item["status"] == "pending" for item in plan))

    def test_live_research_prioritizes_known_official_domains(self):
        module = load("live_research_official_plan_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        plan = module.build_plan("What developer products does Dataify offer?", "US", "12 months", 3)
        self.assertIn("site:dataify.com", plan[0]["query"])
        self.assertTrue(any("site:doc.dataify.com" in item["query"] for item in plan))
        self.assertTrue(any("site:github.com/dataify-server" in item["query"] for item in plan))

    def test_live_research_rejects_sources_unrelated_to_known_entity(self):
        module = load("live_research_entity_gate_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        rows = [
            {
                "source": "https://www.govinfo.gov/water-report",
                "content": "Developer models and products for water resources management. " * 20,
                "angle": "overview",
            },
            {
                "source": "https://www.dataify.com/products",
                "content": "Dataify developer products include web data APIs, MCP, SDKs, and scraping tools. " * 20,
                "angle": "overview",
            },
        ]
        kept, rejected = module.quality_gate_sources(rows, "What developer products does Dataify offer?")
        self.assertEqual(["https://www.dataify.com/products"], [item["source"] for item in kept])
        self.assertEqual("entity_mismatch", rejected[0]["reason"])

    def test_live_research_rejects_sources_unrelated_to_detected_entity(self):
        module = load("live_research_detected_entity_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        rows = [
            {"source": "https://example.com/generic", "content": "Developer products and pricing. " * 20, "angle": "overview"},
            {"source": "https://example.com/acme", "content": "Acme developer products and pricing. " * 20, "angle": "overview"},
        ]
        kept, rejected = module.quality_gate_sources(rows, "What developer products does Acme offer?")
        self.assertEqual(["https://example.com/acme"], [item["source"] for item in kept])
        self.assertEqual("entity_mismatch", rejected[0]["reason"])

    def test_live_research_ranks_known_official_urls_first(self):
        module = load("live_research_official_rank_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        urls = [
            "https://example.com/dataify-review",
            "https://doc.dataify.com/start",
            "https://www.dataify.com/products",
        ]
        self.assertEqual("https://www.dataify.com/products", module.rank_urls(urls, "What is Dataify? ")[0])

    def test_live_research_state_uses_execution_budget_contract(self):
        module = load("research_state_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        with tempfile.TemporaryDirectory() as temp:
            args = module.parser().parse_args(["--question", "market evidence", "--max-actions", "5", "--output-dir", temp])
            _, state = module.load_state(args)
        self.assertEqual(5, state["action_budget"])

    def test_live_research_seeds_known_official_pages_without_search_dependency(self):
        module = load("research_seed_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        with tempfile.TemporaryDirectory() as temp:
            args = module.parser().parse_args([
                "--question", "What developer products does Dataify offer?",
                "--max-actions", "3", "--output-dir", temp,
            ])
            _, state = module.load_state(args)
        fetches = [item for item in state["actions"] if item["type"] == "fetch"]
        self.assertEqual(2, len(fetches))
        self.assertTrue(all(not item.get("depends_on") for item in fetches))
        self.assertEqual("https://www.dataify.com/", fetches[0]["url"])
        self.assertLessEqual(len(state["actions"]), state["action_budget"])

    def test_live_research_distributes_fetch_budget_across_search_angles(self):
        module = load("research_expand_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        actions = module.build_plan("market evidence", "US", "12 months", 3)
        state = {"action_budget": 6, "actions": actions}
        body = json.dumps({"organic": [{"link": "https://example.com/a"}, {"link": "https://example.org/b"}]})
        module.expand(state, actions[0], body)
        self.assertEqual(1, sum(item["type"] == "fetch" for item in state["actions"]))

    def test_live_research_quality_gate_deduplicates_and_rejects_block_pages(self):
        module = load("research_quality_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        rows = [
            {"source": "https://Example.com/a?utm_source=x#top", "content": "Useful evidence " * 40, "angle": "data"},
            {"source": "https://example.com/a", "content": "Duplicate evidence " * 40, "angle": "overview"},
            {"source": "https://blocked.example/", "content": "Just a moment... CAPTCHA", "angle": "risks"},
        ]
        kept, rejected = module.quality_gate_sources(rows, "useful evidence market")
        self.assertEqual(1, len(kept))
        self.assertEqual(2, len(rejected))
        self.assertGreater(kept[0]["quality_score"], 0)

    def test_live_research_brief_never_claims_ready_without_usable_pages(self):
        module = load("research_brief_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        brief = module.build_brief("question", [], [{"reason": "too_short"}], "2026-01-01")
        self.assertEqual("insufficient_evidence", brief["status"])
        self.assertIn("Evidence gaps", brief["markdown"])

    def test_live_research_requires_primary_source_for_official_question(self):
        module = load("research_primary_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        sources = [{"source": "https://blog.example/a", "content": "text " * 100, "quality_score": 0.7, "authority_score": 0.5, "angle": "overview"}, {"source": "https://news.example/b", "content": "text " * 100, "quality_score": 0.6, "authority_score": 0.5, "angle": "current"}]
        self.assertEqual("insufficient_evidence", module.build_brief("official regulation timeline", sources, [], "2026-01-01")["status"])

    def test_live_research_unwraps_and_cleans_readable_page_text(self):
        module = load("research_text_test", ROOT / "skills/dataify-live-research/scripts/run_research.py")
        self.assertEqual("Policy changed in 2026.", module.visible_text('<html><script>noise()</script><p>Policy changed in 2026.</p></html>'))

    def test_search_url_extraction_ignores_metadata_urls(self):
        module = load("dataify_client_test", ROOT / "skills/dataify-task-operations/scripts/dataify_client.py")
        body = json.dumps({"ai_url": "https://google.com/internal", "organic": [{"link": "https://example.com/article"}]})
        self.assertEqual(["https://example.com/article"], module.urls_from_search(body))

    def test_shared_client_retry_is_bounded_and_honors_retry_after(self):
        module = load("dataify_retry_test", ROOT / "skills/dataify-task-operations/scripts/dataify_client.py")
        self.assertEqual(3.0, module.retry_delay(1, "3"))
        self.assertLessEqual(module.retry_delay(99, "999"), 30.0)

    def test_seo_analyzer_reports_material_html_defects(self):
        module = load("seo_test", ROOT / "skills/dataify-seo-audit/scripts/run_seo_audit.py")
        result = module.audit_html("https://example.com", "<html><head><title></title></head><body><h1>A</h1><h1>B</h1></body></html>")
        codes = {item["code"] for item in result["issues"]}
        self.assertIn("missing_title", codes)
        self.assertIn("missing_meta_description", codes)
        self.assertIn("multiple_h1", codes)
        self.assertIn("missing_canonical", codes)

    def test_seo_analyzer_accepts_meta_without_name_or_property(self):
        module = load("seo_meta_test", ROOT / "skills/dataify-seo-audit/scripts/run_seo_audit.py")
        result = module.audit_html(
            "https://example.com",
            '<meta charset="utf-8"><meta content="width=device-width"><title>Example Product Documentation</title><h1>Docs</h1>',
        )
        self.assertEqual("Example Product Documentation", result["title"])

    def test_seo_finding_has_actionable_evidence_contract(self):
        module = load("seo_contract_test", ROOT / "skills/dataify-seo-audit/scripts/run_seo_audit.py")
        result = module.audit_html("https://example.com", "<title>X</title><h1>A</h1>")
        finding = result["issues"][0]
        self.assertTrue({"code", "layer", "priority", "impact", "evidence", "fix"}.issubset(finding))

    def test_seo_parser_checks_hreflang_open_graph_and_internal_links(self):
        module = load("seo_extended_test", ROOT / "skills/dataify-seo-audit/scripts/run_seo_audit.py")
        html = '<title>Useful example product page title</title><meta name="description" content="' + ('a' * 80) + '"><link rel="canonical" href="https://example.com/x"><link rel="alternate" hreflang="en" href="/en"><meta property="og:title" content="OG"><h1>A</h1><a href="/next">Next</a>'
        result = module.audit_html("https://example.com/x", html)
        self.assertEqual(["en"], result["hreflang"])
        self.assertEqual("OG", result["open_graph"]["og:title"])
        self.assertEqual(1, result["internal_link_count"])

    def test_sitemap_sampling_is_stratified_not_prefix_only(self):
        module = load("seo_sample_test", ROOT / "skills/dataify-seo-audit/scripts/run_seo_audit.py")
        urls = [f"https://example.com/blog/{i}" for i in range(8)] + ["https://example.com/pricing", "https://example.com/docs/start"]
        sample = module.stratified_sample("https://example.com/", urls, 4)
        self.assertIn("https://example.com/pricing", sample)
        self.assertTrue(any("/docs/" in url for url in sample))

    def test_scraper_builder_profiles_jsonld_and_pagination(self):
        module = load("builder_test", ROOT / "skills/dataify-scraper-builder/scripts/build_scraper.py")
        html = '<html><head><meta charset="utf-8"><meta content="width=device-width"><script type="application/ld+json">{"name":"A"}</script></head><body><a rel="next" href="?page=2">Next</a></body></html>'
        profile = module.profile_html("https://shop.example/products", html)
        self.assertTrue(profile["json_ld"])
        self.assertTrue(profile["pagination_signals"])
        self.assertEqual("web_unlocker", profile["recommended_route"])

    def test_generated_scraper_supports_common_requested_fields(self):
        module = load("builder_source_test", ROOT / "skills/dataify-scraper-builder/scripts/build_scraper.py")
        source = module.generated_source(["title", "description", "canonical", "h1"])
        compile(source, "generated_scraper.py", "exec")
        self.assertIn('"canonical": parser.canonical', source)
        self.assertIn('"h1": " ".join(parser.h1)', source)

    def test_scraper_builder_routes_prebuilt_without_requiring_token(self):
        module = load("builder_route_test", ROOT / "skills/dataify-scraper-builder/scripts/build_scraper.py")
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {}, clear=True):
            args = module.main.__globals__["argparse"].Namespace(
                url="https://www.amazon.com/dp/B000000000",
                fields="title,price",
                scope="single-page",
                geography="us",
                output_dir=Path(temp),
                dry_run=False,
                force_custom=False,
            )
            self.assertEqual(0, module.run(args))
            result = json.loads((Path(temp) / "scraper_spec.json").read_text(encoding="utf-8"))
        self.assertEqual("routed_to_prebuilt", result["status"])
        self.assertEqual("dataify-amazon-product", result["prebuilt_skill"])

    def test_scraper_builder_marks_interactive_shell_as_browser_required(self):
        module = load("builder_route_shape_test", ROOT / "skills/dataify-scraper-builder/scripts/build_scraper.py")
        profile = module.profile_html("https://example.com/app", '<div id="root"></div><form><input type="password"><button>Log in</button></form>')
        self.assertEqual("browser_required", profile["recommended_route"])

    def test_scraper_builder_validates_requested_field_completeness(self):
        module = load("builder_validation_test", ROOT / "skills/dataify-scraper-builder/scripts/build_scraper.py")
        result = module.validate_sample([{"name": "A", "price": "$10"}, {"name": "B", "price": None}], ["name", "price"])
        self.assertEqual(2, result["record_count"])
        self.assertEqual(0.75, result["field_completeness"])
        self.assertEqual(["price"], result["incomplete_fields"])

    def test_scraper_builder_extracts_requested_jsonld_fields(self):
        module = load("builder_jsonld_test", ROOT / "skills/dataify-scraper-builder/scripts/build_scraper.py")
        html = '<script type="application/ld+json">{"@type":"Product","name":"Camera","offers":{"price":"19.99","priceCurrency":"USD"}}</script>'
        self.assertEqual({"name": "Camera", "price": "19.99", "priceCurrency": "USD"}, module.common_sample(html, ["name", "price", "priceCurrency"]))

    def test_onboarding_health_classifies_auth_and_balance(self):
        module = load("onboarding_health_test", ROOT / "skills/dataify-agent-onboarding/scripts/onboard.py")
        self.assertEqual("ready", module.classify_health({"ok": True, "status": 200})["status"])
        self.assertEqual("invalid_credentials", module.classify_health({"ok": False, "status": 401})["status"])
        self.assertEqual("insufficient_balance", module.classify_health({"ok": False, "status": 402})["status"])

    def test_opt_in_telemetry_drops_sensitive_and_business_data(self):
        module = load("telemetry_test", ROOT / "skills/dataify-agent-onboarding/scripts/telemetry.py")
        clean = module.sanitize({"skill": "onboarding", "event": "completed", "token": "secret", "query": "private goal", "url": "https://private.example"})
        self.assertEqual("onboarding", clean["skill"])
        self.assertNotIn("token", clean)
        self.assertNotIn("query", clean)
        self.assertNotIn("url", clean)

    def test_mcp_capability_resolution_and_redacted_inspection(self):
        module = load("mcp_runtime_test", ROOT / "skills/dataify-mcp/scripts/configure_mcp.py")
        self.assertIn("amazon", module.tools_for_capability("ecommerce"))
        inspected = module.inspect_config({"mcpServers": {"dataify": {"url": "https://mcp.dataify.com/mcp?token=secret&tools=user_info"}}})
        self.assertNotIn("secret", json.dumps(inspected))
        self.assertEqual(["user_info"], inspected["tools"])

    def test_mcp_manual_verify_does_not_skip_protocol_check(self):
        module = load("mcp_manual_test", ROOT / "skills/dataify-mcp/scripts/configure_mcp.py")
        with patch.dict(os.environ, {"DATAIFY_API_TOKEN": "secret"}), patch.object(module, "verify_server", return_value={"status": "ready"}) as verify, patch.object(sys, "argv", ["configure_mcp.py", "--client", "manual", "--verify"]):
            self.assertEqual(0, module.main())
        verify.assert_called_once()

    def test_api_best_practices_has_language_and_api_references(self):
        base = ROOT / "skills/dataify-api-best-practices/references"
        for name in ("authentication.md", "serp-api.md", "web-unlocker.md", "builder-api.md", "task-lifecycle.md", "python.md", "javascript-typescript.md", "error-catalog.md", "production-checklist.md"):
            self.assertTrue((base / name).is_file(), name)

    def test_integration_auditor_finds_unsafe_patterns(self):
        module = load("audit_test", ROOT / "skills/dataify-api-best-practices/scripts/audit_integration.py")
        findings = module.audit_text('TOKEN="abc"\nparser.add_argument("--token")\nwhile True:\n    pass\n', "sample.py")
        codes = {item["code"] for item in findings}
        self.assertIn("command_line_token", codes)
        self.assertIn("unbounded_polling", codes)

    def test_shared_client_copies_are_identical(self):
        canonical = (ROOT / "skills/dataify-task-operations/scripts/dataify_client.py").read_bytes()
        for name in ("dataify-live-research", "dataify-seo-audit", "dataify-scraper-builder"):
            self.assertEqual(canonical, (ROOT / "skills" / name / "scripts/dataify_client.py").read_bytes(), name)

    def test_all_new_scripts_compile(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in SKILLS:
                for script in (ROOT / "skills" / name / "scripts").glob("*.py"):
                    py_compile.compile(str(script), cfile=str(Path(directory) / (name + "-" + script.name + "c")), doraise=True)

    def test_no_token_cli_option_in_new_skills(self):
        for name in SKILLS:
            for path in (ROOT / "skills" / name).rglob("*"):
                if path.is_file() and path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".json"}:
                    self.assertNotIn("--token", path.read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
