#!/usr/bin/env python
"""Minimal Flask test."""
from flask import Flask, render_template

app = Flask(__name__, template_folder='dashboard/templates')

@app.route('/')
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        html = render_template('index.html')
        print(f"Template size: {len(html)} bytes")
        print(f"Has 'Generated Images': {'Generated Images' in html}")
        print(f"Has 'generated-images': {'generated-images' in html}")
        print(f"Has 'renderGeneratedImages': {'renderGeneratedImages' in html}")
        
        # Count sections
        import re
        sections = re.findall(r'<section class="mb-8">', html)
        print(f"Number of <section> elements: {len(sections)}")
        
        # Find the Generated Images section
        if '<h2' in html:
            h2_count = len(re.findall(r'<h2[^>]*>', html))
            print(f"Number of <h2> elements: {h2_count}")
