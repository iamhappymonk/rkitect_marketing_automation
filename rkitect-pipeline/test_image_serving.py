#!/usr/bin/env python
"""Test image serving route."""
import httpx

# Test LinkedIn image
r = httpx.head(
    "http://127.0.0.1:5050/output/2026-05-18/linkedin_image.jpg",
    auth=("admin", "pass")
)
print(f"LinkedIn Image - Status: {r.status_code}, Content-Type: {r.headers.get('content-type')}")

# Test carousel slide
r = httpx.head(
    "http://127.0.0.1:5050/output/2026-05-18/carousel_images/slide_01.jpg",
    auth=("admin", "pass")
)
print(f"Carousel Slide 1 - Status: {r.status_code}, Content-Type: {r.headers.get('content-type')}")

# Test API data endpoint
r = httpx.get(
    "http://127.0.0.1:5050/api/data",
    auth=("admin", "pass")
)
print(f"\n/api/data - Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Response keys: {list(data.keys())}")
    if "images" in data:
        print(f"Images in response: {data['images']}")
        if data["images"]:
            print("✓ Images found in API response:")
            for key in data["images"]:
                print(f"  - {key}: {type(data['images'][key])}")
        else:
            print("✗ Images dict is empty")
    else:
        print("✗ No 'images' key in API response")
