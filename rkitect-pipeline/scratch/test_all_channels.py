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

channels = {
    "linkedin":  BUFFER_PROFILES["linkedin"],   # 6a020577090476fb990aecc6
    "twitter":   BUFFER_PROFILES["twitter"],     # 6a02054e090476fb990aec04
    "instagram": BUFFER_PROFILES["instagram"],   # 6a020514090476fb990aeaf3
}

for platform, channel_id in channels.items():
    print(f"\n=== Scheduling to {platform} (channel: {channel_id}) ===")
    r = httpx.post(
        "https://api.buffer.com/1/graphql",
        json={
            "query": query,
            "variables": {
                "channelId": channel_id,
                "text": f"[TEST] rkitect.ai pipeline scheduling test for {platform} channel 🚀",
                "schedulingType": "automatic",
                "mode": "addToQueue"
            }
        },
        headers={"Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"},
        timeout=15,
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
