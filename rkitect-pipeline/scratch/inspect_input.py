import httpx
import json

query = """
query {
  __type(name: "CreatePostInput") {
    name
    inputFields {
      name
      type {
        name
        kind
        ofType {
          name
          kind
        }
      }
    }
  }
}
"""

r = httpx.post(
    "https://api.buffer.com/1/graphql",
    headers={"Authorization": "Bearer WsaN6pD6roKFLYXbK0Djdw1aeqXksGeFHVCYwg_0UUw"},
    json={"query": query}
)
print(json.dumps(r.json(), indent=2))
