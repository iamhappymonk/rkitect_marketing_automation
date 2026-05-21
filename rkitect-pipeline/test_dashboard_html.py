#!/usr/bin/env python
"""Test the dashboard by directly fetching and parsing the HTML."""
import httpx

# Get the dashboard HTML
r = httpx.get(
    "http://127.0.0.1:5050/",
    auth=("admin", "pass")
)

print(f"Status: {r.status_code}")

if r.status_code == 200:
    html = r.text
    print(f"HTML length: {len(html)} bytes")
    
    # Save to file for inspection
    with open("served_index.html", "w") as f:
        f.write(html)
    print("HTML saved to served_index.html")
    
    # Check if the Generated Images section is in the HTML
    if 'generated-images' in html:
        print("✓ generated-images found in HTML")
        # Extract surrounding text
        idx = html.find('generated-images')
        print(html[max(0, idx-100):idx+100])
    else:
        print("✗ generated-images NOT in HTML")
        # Look for Image Briefs instead
        if 'Image Briefs' in html:
            print("  But Image Briefs IS found")
    
    # Check if renderGeneratedImages is in the JavaScript
    if 'renderGeneratedImages' in html:
        print("✓ renderGeneratedImages function found in JavaScript")
    else:
        print("✗ renderGeneratedImages function NOT in JavaScript")
        if 'renderImageBriefs' in html:
            print("  But renderImageBriefs IS found")
