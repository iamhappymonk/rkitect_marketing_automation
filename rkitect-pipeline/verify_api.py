#!/usr/bin/env python
"""Direct API test from dashboard module."""
import sys
from pathlib import Path

# Set Python path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

# Import dashboard functions directly
from dashboard.app import get_today_output, get_today_images, api_data, app

# Test data
print("=== Testing get_today_images() ===")
images = get_today_images()
print(f"Images found: {bool(images)}")
if images:
    print(f"Image types: {list(images.keys())}")

print("\n=== Testing API function ===")
# Test the api_data function directly
with app.app_context():
    try:
        result = api_data()
        # Get the JSON data
        import json
        data = json.loads(result.data)
        print(f"API keys: {list(data.keys())}")
        print(f"Has 'images': {'images' in data}")
        if 'images' in data:
            print(f"Images in API: {list(data['images'].keys())}")
    except Exception as e:
        print(f"Error: {e}")
