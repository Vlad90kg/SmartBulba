from dotenv import load_dotenv
import os

load_dotenv()

PUBNUB_SUB_KEY = os.getenv("PUBNUB_SUB_KEY", "").strip()
PUBNUB_PUB_KEY = os.getenv("PUBNUB_PUB_KEY", "").strip()
PUBNUB_CHANNEL = os.getenv("PUBNUB_CHANNEL", "room-activity").strip()


TAPO_USERNAME = os.getenv("TAPO_USERNAME")
TAPO_PASSWORD = os.getenv("TAPO_PASSWORD")
SHELLY_MAC = os.getenv("SHELLY_MAC")

BRIGHTNESS_MAP = {
    "low": 30,
    "medium": 60,
    "high": 100
}

MOTION_TIMEOUT = 30
BRIGHTNESS = 100







