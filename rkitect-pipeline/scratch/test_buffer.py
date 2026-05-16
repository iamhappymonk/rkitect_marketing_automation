import httpx
print(httpx.post('https://api.buffer.com/1/graphql', headers={'Authorization': 'Bearer WsaN6pD6roKFLYXbK0Djdw1aeqXksGeFHVCYwg_0UUw'}, json={'query': 'mutation { createIdea(input: { organizationId: "6a020497c24e5c8354f656e3", content: { title: "Title", text: "Text" } }) { ... on Idea { id } } }'}).status_code)
