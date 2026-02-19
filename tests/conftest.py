from __future__ import annotations

import sys
from pathlib import Path

# Allow tests to import codegen tooling under tools/ without package installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
