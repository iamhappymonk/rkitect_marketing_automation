#!/usr/bin/env python
"""Quick test to verify Flask template is served correctly."""
import httpx

try:
    r = httpx.get('http://127.0.0.1:5050/', auth=('admin', 'pass'), timeout=5)
    print(f"Status: {r.status_code}")
    print(f"HTML size: {len(r.text)} bytes")
    print(f"Has 'Generated Images': {'Generated Images' in r.text}")
    print(f"Has 'renderGeneratedImages': {'renderGeneratedImages' in r.text}")
except Exception as e:
    print(f"Connection error: {e}")
