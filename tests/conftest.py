"""Shared pytest configuration for the test suite."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
src_path = PROJECT_ROOT / "src"
sys.path.insert(0, str(src_path))
