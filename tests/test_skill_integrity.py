import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


class SkillIntegrityTests(unittest.TestCase):
    def _skill_descriptions(self):
        descriptions = {}
        for skill in ROOT.glob("skills/*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            name = next(line.split(":", 1)[1].strip().strip('"') for line in text.splitlines() if line.startswith("name:"))
            description = next(line.split(":", 1)[1].strip().strip('"') for line in text.splitlines() if line.startswith("description:"))
            descriptions[name] = description
        return descriptions

    def test_trigger_descriptions_are_concise_and_user_facing(self):
        descriptions = self._skill_descriptions()
        forbidden_internal = (
            "successful Dataify scraper detail entry",
            "getToolParams",
            "DATAIFY_API_TOKEN",
            "task_id",
            "task status",
            "troubleshoot",
        )
        for name, description in descriptions.items():
            self.assertLessEqual(len(description), 500, name)
            if name.startswith("dataify-") and name not in {
                "dataify-router", "dataify-task-operations", "dataify-task-status", "dataify-task-result"
            }:
                for phrase in forbidden_internal:
                    self.assertNotIn(phrase, description, name)

    def test_trigger_descriptions_have_required_boundaries(self):
        descriptions = self._skill_descriptions()
        boundary_skills = {
            "dataify-youtube-video-by-url",
            "dataify-youtube-video-post",
            "dataify-youtube-product-by-id",
            "dataify-google-maps",
            "dataify-google-map-details",
            "dataify-google-shopping",
            "dataify-google-shopping-keywords",
            "dataify-amazon-product",
            "dataify-amazon-product-list",
            "dataify-amazon-global-product",
        }
        for name in boundary_skills:
            self.assertIn("Do not use", descriptions[name], name)

    def test_google_shopping_trigger_has_no_instagram_contamination(self):
        description = self._skill_descriptions()["dataify-google-shopping-keywords"].lower()
        self.assertNotIn("instagram", description)
        self.assertNotIn("reel", description)

    def test_trigger_case_dataset_covers_expected_and_forbidden_routes(self):
        descriptions = self._skill_descriptions()
        dataset = json.loads((ROOT / "config" / "skill-trigger-cases.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(dataset["cases"]), 18)
        for case in dataset["cases"]:
            self.assertIn(case["expected"], descriptions, case)
            self.assertTrue(case["forbidden"], case)
            for name in case["forbidden"]:
                self.assertIn(name, descriptions, case)

    def test_competitive_intelligence_has_positive_and_negative_routes(self):
        descriptions = self._skill_descriptions()
        dataset = json.loads((ROOT / "config" / "skill-trigger-cases.json").read_text(encoding="utf-8"))
        cases = dataset["cases"]
        positives = [case for case in cases if case["expected"] == "dataify-competitive-intelligence"]
        negatives = [case for case in cases if "dataify-competitive-intelligence" in case["forbidden"]]
        self.assertGreaterEqual(len(positives), 3)
        self.assertGreaterEqual(len(negatives), 3)
        description = descriptions["dataify-competitive-intelligence"]
        self.assertIn("Do not use", description)
        self.assertIn("competitor", description.lower())

    def test_repository_validator(self):
        spec = importlib.util.spec_from_file_location("validate_skills", ROOT / "scripts" / "validate_skills.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        self.assertEqual([], module.validate(ROOT))

    def test_trigger_validator(self):
        spec = importlib.util.spec_from_file_location(
            "validate_skill_triggers", ROOT / "scripts" / "validate_skill_triggers.py"
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        self.assertEqual([], module.validate())

    def test_parameter_interaction_policy_is_progressive(self):
        forbidden = (
            "Always display submitted parameters as a Markdown table",
            "Before every real API call, show a Markdown confirmation table",
            "Do not call the API until the user explicitly confirms the table",
            "show the user the required values, optional values, and defaults",
            "始终以 Markdown 表格展示",
            "提交前，向用户展示参数清单中列出的必填值、可选值和默认值",
            "当用户调用此技能时，首先告知这些值的使用情况",
            "先把选项展示给用户，再生成最终请求",
            "user confirms the parameter table",
            "complete field list",
            "The table must have exactly",
            "用户确认后才能调用 API",
            "用户确认前不要调用 API",
            "完整字段列表",
            "表格必须恰好包含",
        )
        for skill in ROOT.glob("skills/*/SKILL*.md"):
            text = skill.read_text(encoding="utf-8")
            if skill.name == "SKILL.md":
                self.assertIn("## Parameter interaction policy", text, skill)
                self.assertIn("execute immediately", text, skill)
                self.assertIn("internal implementation parameters", text, skill)
            for phrase in forbidden:
                self.assertNotIn(phrase, text, skill)

    def test_read_only_search_scripts_do_not_require_confirmation_flag(self):
        for script in ROOT.glob("skills/serp-*/scripts/*.py"):
            text = script.read_text(encoding="utf-8")
            self.assertNotIn("if not args.confirmed", text, script)
            self.assertNotIn("if not getattr(args, \"confirmed\"", text, script)

    def test_parameter_policy_generator_is_current(self):
        spec = importlib.util.spec_from_file_location(
            "sync_parameter_interaction", ROOT / "scripts" / "sync_parameter_interaction.py"
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        self.assertEqual(0, module.synchronize(check=True))

    def test_required_targets_never_fall_back_to_documentation_examples(self):
        target_defaults = (
            "DEFAULT_URL", "DEFAULT_URLS", "DEFAULT_CATEGORY_URL", "DEFAULT_KEYWORD",
            "DEFAULT_KEYWORDS", "DEFAULT_VIDEO_ID", "DEFAULT_POSTURL", "DEFAULT_PROFILEURL", "DEFAULT_USERNAME", "DEFAULT_LISTURL", "DEFAULT_SKU",
        )
        fallback_patterns = (" or [DEFAULT_", ".get(\"url\", DEFAULT_", ".get(\"keyword\", DEFAULT_",
                             ".get(\"video_id\", DEFAULT_", ".get(\"posturl\", DEFAULT_",
                             ".get(\"profileurl\", DEFAULT_", ".get(\"username\", DEFAULT_", ".get(\"sku\", DEFAULT_")
        for script in ROOT.glob("skills/scraper-*/scripts/*.py"):
            text = script.read_text(encoding="utf-8")
            for pattern in fallback_patterns:
                self.assertNotIn(pattern, text, script)
            for name in target_defaults:
                self.assertNotRegex(text, rf"add_argument\([^\n]+default={name}\b", script)

    def test_business_docs_have_no_legacy_confirmation_or_token_conflicts(self):
        forbidden = (
            "only after parameter confirmation",
            "do not poll for results after builder succeeds",
            "user-provided token",
            "ask the user to provide the token",
            "--token user_token",
            "--token \"user_token\"",
        )
        for skill in ROOT.glob("skills/*/SKILL*.md"):
            text = skill.read_text(encoding="utf-8").lower()
            self.assertNotIn("--token", text, skill)
            self.assertNotIn("only after showing it in the parameter confirmation table", text, skill)
            self.assertNotIn("if the user provides a token", text, skill)
            self.assertNotIn("confirmation table", text, skill)
            self.assertNotIn("ask the user to provide a token", text, skill)
            for phrase in forbidden:
                self.assertNotIn(phrase, text, skill)

    def test_all_catalog_builder_scripts_use_the_shared_completion_runtime(self):
        scripts = list(ROOT.glob("skills/scraper-*/scripts/build-dataify-request.py"))
        self.assertEqual(8, len(scripts))
        for script in scripts:
            text = script.read_text(encoding="utf-8")
            self.assertIn("run_catalog_builder", text, script)

    def test_all_main_skills_have_one_command_quick_start(self):
        for skill in ROOT.glob("skills/*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            self.assertIn("## Quick Start", text, skill)
            self.assertIn("```", text.split("## Quick Start", 1)[1], skill)

        snapshot = json.loads((ROOT / "config" / "clawhub-top-skills.json").read_text(encoding="utf-8"))
        for item in snapshot["skills"]:
            text = (ROOT / "skills" / item["local_skill"] / "SKILL.md").read_text(encoding="utf-8")
            quick_start = text.split("## Quick Start", 1)[1].split("\n## ", 1)[0]
            self.assertNotIn("--help", quick_start, item["local_skill"])

    def test_serp_skills_default_to_user_facing_results(self):
        for skill in ROOT.glob("skills/serp-*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            self.assertIn("## Result presentation", text, skill)
            self.assertIn("raw JSON", text, skill)

    def test_maps_family_has_explicit_trigger_boundaries(self):
        expected = {
            "serp-google-local": "local pack",
            "serp-google-maps": "coordinates",
            "scraper-google-map-details": "Place ID",
            "scraper-google-maps-reviews": "reviews",
        }
        for folder, boundary in expected.items():
            text = (ROOT / "skills" / folder / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(boundary, text, folder)

    def test_skill_entrypoints_use_progressive_disclosure(self):
        for skill in ROOT.glob("skills/*/SKILL.md"):
            self.assertLessEqual(len(skill.read_text(encoding="utf-8").splitlines()), 220, skill)

    def test_shared_catalog_builder_rejects_missing_required_targets(self):
        runtime_dir = ROOT / "skills" / "dataify-task-operations" / "scripts"
        sys.path.insert(0, str(runtime_dir))
        try:
            spec = importlib.util.spec_from_file_location("catalog_builder", runtime_dir / "catalog_builder.py")
            module = importlib.util.module_from_spec(spec)
            assert spec.loader
            spec.loader.exec_module(module)
        finally:
            sys.path.remove(str(runtime_dir))
        tool = {"params": [{"param": "url", "required": True}]}
        with self.assertRaisesRegex(ValueError, "missing required values: url"):
            module.validate_required(tool, [{}])

    def test_builder_helper_does_not_print_token(self):
        script = ROOT / "skills" / "scraper-airbnb-product-by-searchurl" / "scripts" / "build-dataify-request.py"
        spec = importlib.util.spec_from_file_location("builder_helper", script)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        tool = {"spider_name": "airbnb.com", "tool_sign": "airbnb_product_by-searchurl"}
        with patch.dict(os.environ, {"DATAIFY_API_TOKEN": "secret-token"}):
            command = module.build_curl(tool, json.dumps([{"url": "https://example.com"}]))
        self.assertNotIn("secret-token", command)
        self.assertIn("$DATAIFY_API_TOKEN", command)

    def test_builder_submission_scripts_complete_by_default(self):
        builders = set()
        request_only = set(ROOT.glob("skills/scraper-*/scripts/build-dataify-request.py"))
        for script in ROOT.glob("skills/scraper-*/scripts/*.py"):
            text = script.read_text(encoding="utf-8")
            if "scraperapi.dataify.com/builder" in text or "BUILDER_URL" in text:
                builders.add(script)

        submitters = builders - request_only
        self.assertEqual(29, len(submitters))
        for script in submitters:
            text = script.read_text(encoding="utf-8")
            self.assertIn("--no-wait", text, script)
            self.assertIn("complete_task", text, script)

    def test_public_docs_do_not_expose_api_token_argument(self):
        for path in [ROOT / "README.md", *ROOT.glob("skills/*/SKILL*.md")]:
            self.assertNotIn("--api-token", path.read_text(encoding="utf-8"), path)

    def test_mcp_setup_does_not_accept_tokens_on_the_command_line(self):
        for path in (ROOT / "README.md", ROOT / "setup-mcp.sh"):
            self.assertNotIn("--token", path.read_text(encoding="utf-8"), path)

    def test_scraper_skills_have_no_legacy_completion_conflicts(self):
        forbidden = (
            "Stop after Builder succeeds",
            "Do not download result files",
            "Builder 成功后停止",
        )
        for path in ROOT.glob("skills/scraper-*/SKILL*.md"):
            text = path.read_text(encoding="utf-8")
            for phrase in forbidden:
                self.assertNotIn(phrase, text, path)

    def test_top_downloaded_skills_have_quick_starts(self):
        snapshot = json.loads((ROOT / "config" / "clawhub-top-skills.json").read_text(encoding="utf-8"))
        self.assertEqual(15, len(snapshot["skills"]))
        for item in snapshot["skills"]:
            skill = ROOT / "skills" / item["local_skill"] / "SKILL.md"
            self.assertIn("## Quick Start", skill.read_text(encoding="utf-8"), skill)

    def test_generated_product_messaging_is_current(self):
        spec = importlib.util.spec_from_file_location(
            "sync_product_messaging", ROOT / "scripts" / "sync_product_messaging.py"
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        self.assertEqual(0, module.synchronize(check=True))

    def test_generated_trigger_descriptions_are_current(self):
        spec = importlib.util.spec_from_file_location(
            "sync_skill_triggers", ROOT / "scripts" / "sync_skill_triggers.py"
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        self.assertEqual(0, module.synchronize(check=True))

    def test_all_skills_include_cross_platform_token_recovery(self):
        for skill in ROOT.glob("skills/*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            self.assertIn("Detect the current operating system and shell", text, skill)
            self.assertIn("Never ask the user to paste the token into chat", text, skill)
            self.assertIn("continue the original task", text, skill)


if __name__ == "__main__":
    unittest.main()
