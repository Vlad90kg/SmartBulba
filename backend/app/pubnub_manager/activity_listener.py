from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
import os


class ActivityListener(SubscribeCallback):
    def message(self, pubnub, message):
        print(f"--- [PAM ACTIVE] ACTIVITY EVENT: {message.message} ---")


def start_activity_listener():
    config = PNConfiguration()
    config.subscribe_key = os.getenv("PN_SUB_KEY")
    config.publish_key = os.getenv("PN_PUB_KEY")
    config.secret_key = os.getenv("PN_SEC_KEY")  # Права админа
    config.user_id = "aws_backend_listener"
    config.secure = True

    pubnub = PubNub(config)

    activity_ch = os.getenv("PUBNUB_ACTIVITY_CHANNEL")
    control_ch = os.getenv("PUBNUB_CONTROL_CHANNEL")

    print(f"PAM: Granting access to {activity_ch} and {control_ch}...")
    pubnub.grant().channels([activity_ch, control_ch]).read(True).write(True).ttl(1440).sync()

    pubnub.add_listener(ActivityListener())
    pubnub.subscribe().channels(activity_ch).execute()
    print("Listener is running...")