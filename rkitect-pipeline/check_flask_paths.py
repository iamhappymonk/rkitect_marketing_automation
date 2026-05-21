#!/usr/bin/env python
"""Check Flask template paths."""
import sys
from pathlib import Path

# Set Python path like app.py does
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from flask import Flask

# Create app exactly like dashboard does
app = Flask(__name__)

print(f"App instance: {app}")
print(f"Root path: {app.root_path}")
print(f"Template folder setting: {app.template_folder}")

# Calculate actual template folder path
if app.template_folder:
    template_path = Path(app.root_path) / app.template_folder
else:
    template_path = Path(app.root_path) / "templates"

print(f"Resolved template path: {template_path}")
print(f"Template path exists: {template_path.exists()}")

if template_path.exists():
    for f in sorted(template_path.glob("*.html")):
        size = f.stat().st_size
        has_generated = b"Generated Images" in f.read_bytes()
        print(f"  {f.name}: {size} bytes, has Generated Images: {has_generated}")
