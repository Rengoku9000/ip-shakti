"""Root runner wrapper for test_knowledge_schema"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "drugvista" / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))
from test_knowledge_schema import *

if __name__ == "__main__":
    import unittest
    unittest.main()
