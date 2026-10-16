import os

from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

load_dotenv()

ROOM = os.getenv("LIVEKIT_ROOM", "mi-sala")
IDENTITY = os.getenv("LIVEKIT_IDENTITY", "user-test")
NAME = os.getenv("LIVEKIT_NAME", "Usuario Test")

token = (
    AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET"))
    .with_identity(IDENTITY)
    .with_name(NAME)
    .with_grants(VideoGrants(room_join=True, room=ROOM))
    .to_jwt()
)

print(f"\nLiveKit Server URL:\n{os.getenv('LIVEKIT_URL')}\n")
print(f"Room: {ROOM}")
print(f"\nToken:\n{token}\n")
