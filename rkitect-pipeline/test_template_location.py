#!/usr/bin/env python
"""Test where Flask is loading the template from."""
from pathlib import Path
from flask import Flask, render_template

# Create app exactly like dashboard/app.py does
app = Flask(__name__)

# Check template folder
print(f"Template folder: {app.template_folder}")
print(f"Template path (abs): {app.jinja_loader.searchpath if app.jinja_loader else 'None'}")

# List files in template folder
template_path = Path(app.template_folder) if app.template_folder else None
if template_path and template_path.exists():
    print(f"Files in {template_path}:")
    for f in template_path.glob("*.html"):
        print(f"  - {f.name}")
        
# Try to render and check output
with app.app_context():
    html = render_template("index.html")
    print(f"\nRendered HTML length: {len(html)}")
    print(f"Has 'Generated Images': {'Generated Images' in html}")
    print(f"Has 'Image Briefs': {'Image Briefs' in html}")
    print(f"Has 'generated-images': {'generated-images' in html}")
