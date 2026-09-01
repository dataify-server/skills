#!/usr/bin/env python3
import os
import sys

TASK_RUNTIME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dataify-task-operations", "scripts"))
if TASK_RUNTIME_DIR not in sys.path:
    sys.path.insert(0, TASK_RUNTIME_DIR)

from catalog_builder import build_curl, run_catalog_builder


if __name__ == "__main__":
    raise SystemExit(run_catalog_builder(os.path.dirname(__file__)))
