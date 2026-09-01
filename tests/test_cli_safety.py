import contextlib
import io
import os
from pathlib import Path
import runpy
import json
import shlex
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


class CliSafetyTests(unittest.TestCase):
    def test_no_argument_live_clients_never_reach_the_network(self):
        scripts = []
        for script in ROOT.glob("skills/*/scripts/*.py"):
            text = script.read_text(encoding="utf-8")
            if "urllib.request" in text and 'if __name__ == "__main__"' in text:
                scripts.append(script)

        attempted = []
        offenders = []
        crashes = []

        def reject_network(*args, **kwargs):
            attempted.append(str(args[0]) if args else "unknown")
            raise AssertionError("network call attempted without a business target")

        for script in scripts:
            attempted.clear()
            old_argv = sys.argv
            old_cwd = os.getcwd()
            sys.argv = [str(script)]
            try:
                os.chdir(script.parent.parent)
                with mock.patch.dict(os.environ, {"DATAIFY_API_TOKEN": "invalid-test-token"}, clear=False):
                    with mock.patch("urllib.request.urlopen", side_effect=reject_network):
                        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                            try:
                                runpy.run_path(str(script), run_name="__main__")
                            except (SystemExit, ValueError, RuntimeError, AssertionError):
                                pass
                            except Exception as exc:
                                crashes.append("{}: {}: {}".format(script.relative_to(ROOT), type(exc).__name__, exc))
            finally:
                sys.argv = old_argv
                os.chdir(old_cwd)
            if attempted:
                offenders.append(str(script.relative_to(ROOT)))
        self.assertEqual(
            ([], []),
            (offenders, crashes),
            "Network attempts: {} | crashes: {}".format(", ".join(offenders), "; ".join(crashes)),
        )

    def test_core_quick_starts_parse_and_fail_cleanly_without_token(self):
        snapshot = json.loads((ROOT / "config" / "clawhub-top-skills.json").read_text(encoding="utf-8"))
        failures = []
        for item in snapshot["skills"]:
            skill_dir = ROOT / "skills" / item["local_skill"]
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            block = text.split("## Quick Start", 1)[1].split("```bash", 1)[1].split("```", 1)[0]
            command = " ".join(line.strip().rstrip("\\").strip() for line in block.splitlines() if line.strip() and not line.lstrip().startswith("#"))
            try:
                argv = shlex.split(command)
            except ValueError as exc:
                failures.append("{}: invalid shell quoting: {}".format(item["local_skill"], exc))
                continue
            if argv and argv[0] == "export" and len(argv) > 2 and argv[1].startswith("DATAIFY_API_TOKEN="):
                argv = argv[2:]
            if len(argv) < 2 or argv[0] not in {"python", "python3"}:
                failures.append("{}: Quick Start is not a Python command: {}".format(item["local_skill"], command))
                continue
            if not (skill_dir / argv[1]).is_file():
                failures.append("{}: script does not exist: {}".format(item["local_skill"], argv[1]))
                continue
            env = dict(os.environ)
            env.pop("DATAIFY_API_TOKEN", None)
            completed = subprocess.run(argv, cwd=skill_dir, env=env, text=True, capture_output=True, timeout=10)
            output = completed.stdout + completed.stderr
            if completed.returncode == 0 or "Traceback" in output or "unrecognized arguments" in output:
                failures.append("{}: rc={} output={}".format(item["local_skill"], completed.returncode, output[-300:]))
        self.assertEqual([], failures, "; ".join(failures))


if __name__ == "__main__":
    unittest.main()
