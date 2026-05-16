import httpx, json

ZERNIO_API_KEY = "sk_d6d564778a06d9d25b39207ccc5e21f472ebf09af8526e2c95f6ca04b589336a"
BASE = "https://zernio.com/api/v1"

# 1. List profiles
print("=== Zernio Profiles ===")
r = httpx.get(f"{BASE}/profiles", headers={"Authorization": f"Bearer {ZERNIO_API_KEY}"}, timeout=15)
print(r.status_code)
print(json.dumps(r.json(), indent=2)[:3000])

# 2. List accounts with profileId
data = r.json()
profiles = data.get("profiles", [])
if profiles:
    pid = profiles[0]["_id"]
    print(f"\n=== Accounts for profile {pid} ===")
    r2 = httpx.get(f"{BASE}/accounts?profileId={pid}", headers={"Authorization": f"Bearer {ZERNIO_API_KEY}"}, timeout=15)
    print(r2.status_code)
    print(json.dumps(r2.json(), indent=2)[:3000])
