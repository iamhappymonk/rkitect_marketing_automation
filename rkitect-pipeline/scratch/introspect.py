import httpx
import json

query = """
query IntrospectionQuery {
  __schema {
    mutationType {
      fields {
        name
        description
        args {
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
  }
}
"""

r = httpx.post(
    "https://api.buffer.com/1/graphql",
    headers={"Authorization": "Bearer WsaN6pD6roKFLYXbK0Djdw1aeqXksGeFHVCYwg_0UUw"},
    json={"query": query}
)
with open("schema_mutations.json", "w") as f:
    json.dump(r.json(), f, indent=2)
print("Saved schema mutations")
