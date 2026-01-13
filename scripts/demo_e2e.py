import os, time, json, requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "dev-token")
headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

print("Checking backend health...")
print(requests.get(f"{BACKEND_URL}/health").json())

print("Running sample chat query...")
resp = requests.post(f"{BACKEND_URL}/chat", json={"message": "List top floats by profiles and show a map", "generate_sql": True, "visualize": True}, headers=headers, timeout=60)
print(resp.status_code)
print(json.dumps(resp.json(), indent=2)[:800])

print("Export CSV (first 5 lines)...")
csv_text = requests.get(f"{BACKEND_URL}/export?format=csv").text
print("\n".join(csv_text.splitlines()[:5]))
