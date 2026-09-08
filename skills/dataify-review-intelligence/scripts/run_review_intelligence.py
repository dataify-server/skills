#!/usr/bin/env python3
import os
import sys

RUNTIME = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dataify-task-operations", "scripts"))
if RUNTIME not in sys.path:
    sys.path.insert(0, RUNTIME)
from business_workflow import run



def _configure_utf8_output():
    import sys
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError):
                pass

if __name__ == "__main__":
    _configure_utf8_output()
    raise SystemExit(run("review"))
