#!/usr/bin/env python3
"""Build self-contained ClawHub folders from canonical shared sources."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
def build(output):
    output = output.resolve()
    if output == ROOT or ROOT in output.parents and output.parts[len(ROOT.parts)] == 'skills':
        raise ValueError('Release output must not overlap source skills')
    runtime = ROOT / 'skills/dataify-task-operations/scripts'
    for skill in sorted((ROOT / 'skills').iterdir()):
        if not (skill / 'SKILL.md').exists():
            continue
        target = output / skill.name
        if target.exists():
            raise ValueError('Use a fresh release directory: ' + str(target))
        shutil.copytree(skill, target, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        scripts = target / 'scripts'
        if scripts.exists():
            for source in runtime.glob('*.py'):
                if not (scripts / source.name).exists():
                    shutil.copy2(source, scripts / source.name)
            for source in scripts.glob('*.py'):
                compile(source.read_text(encoding='utf-8'), str(source), 'exec')
        if skill.name in {'dataify-price-intelligence','dataify-review-intelligence','dataify-lead-intelligence','dataify-brand-monitoring'}:
            dependencies = target / '_dependencies/skills'
            for name in ('dataify-task-operations','scraper-amazon-comment'):
                shutil.copytree(ROOT / 'skills' / name, dependencies / name, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    print(str(output))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    build(parser.parse_args().output)
