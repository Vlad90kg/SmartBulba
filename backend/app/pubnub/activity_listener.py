from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
import os

class ActivityListener(SubscribeCallback):
    def message(self, pubnub, message):
        print("📥 ACTIVITY EVENT:", message.message)

def start_activity_listener():
    config = PNConfiguration()
    config.subscribe_key = os.getenv("PN_SUB_KEY")
    config.user_id = "aws_backend_listener"

    pubnub = PubNub(config)

    pubnub.add_listener(ActivityListener())
    pubnub.subscribe().channels(
        os.getenv("PUBNUB_ACTIVITY_CHANNEL")
    ).execute()