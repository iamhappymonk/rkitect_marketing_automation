import httpx
import json

query = """
query {
  t1: __type(name: "SchedulingType") {
    enumValues { name }
  }
  t2: __type(name: "ShareMode") {
    enumValues { name }
  }
}
"""

r = httpx.post(
    "https://api.buffer.com/1/graphql",
    headers={"Authorization": "Bearer WsaN6pD6roKFLYXbK0Djdw1aeqXksGeFHVCYwg_0UUw"},
    json={"query": query}
)
print(json.dumps(r.json(), indent=2))
