import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
STORE_DIR = os.path.join(PROJECT_ROOT, "src", "store")

os.makedirs(OUTPUT_DIR, exist_ok=True)