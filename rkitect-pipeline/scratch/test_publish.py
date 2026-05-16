import sys
from pathlib import Path

# Add the pipeline root to the path so we can import from agents
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from agents.publish import _post_to_buffer

print("Sending test post to Buffer Ideas via GraphQL...")
result = _post_to_buffer(
    profile_id="test_ignored",
    text="This is a test post from the rkitect.ai pipeline to verify the GraphQL Buffer API integration! 🚀",
    platform="linkedin"
)

print("\nResult:")
print(result)
