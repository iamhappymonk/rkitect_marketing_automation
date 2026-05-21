#!/usr/bin/env python
"""Direct test of the api_data response."""
import sys
sys.path.insert(0, '.')

from dashboard.app import app, api_data

# Create a test client
client = app.test_client()

# Test the /api/data endpoint
resp = client.get('/api/data', auth=('admin', 'pass'))
print(f"Status: {resp.status_code}")
print(f"Response type: {type(resp.json)}")

data = resp.get_json()
print(f"\nResponse keys: {list(data.keys())}")
print(f"Has 'images': {'images' in data}")

if 'images' in data:
    print(f"Images value: {data['images']}")
else:
    print("\nDirect function call:")
    from dashboard.app import get_today_images
    images = get_today_images()
    print(f"get_today_images() returns: {images}")
