"""Root runner wrapper for test_jurisdiction_filter"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "drugvista" / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))
from test_jurisdiction_filter import *

if __name__ == "__main__":
    import unittest
    unittest.main()
