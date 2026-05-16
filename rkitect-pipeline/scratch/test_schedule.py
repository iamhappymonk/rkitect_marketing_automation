import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
from config import BUFFER_ACCESS_TOKEN, BUFFER_PROFILES

query = """
mutation CreatePost($channelId: ChannelId!, $text: String!, $schedulingType: SchedulingType!, $mode: ShareMode!) {
  createPost(input: {
    channelId: $channelId,
    text: $text,
    schedulingType: $schedulingType,
    mode: $mode,
    saveToDraft: false
  }) {
    ... on PostActionSuccess {
      post {
        id
      }
    }
  }
}
"""

print("Sending test post to Buffer queue via GraphQL createPost...")
r = httpx.post(
    "https://api.buffer.com/1/graphql",
    json={
        "query": query,
        "variables": {
            "channelId": BUFFER_PROFILES["linkedin"],
            "text": "This is a scheduled post test directly to the queue! 🚀",
            "schedulingType": "automatic",
            "mode": "addToQueue"
        }
    },
    headers={"Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"},
    timeout=10,
)

print(r.status_code)
print(r.text)
