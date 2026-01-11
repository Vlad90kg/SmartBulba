from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from backend.app.models.activity import ActivityModel
import os


class LightController:
    def __init__(self):
        pn_config = PNConfiguration()
        pn_config.publish_key = os.getenv("PN_PUB_KEY")
        pn_config.subscribe_key = os.getenv("PN_SUB_KEY")
        pn_config.user_id = "aws_backend"
        # pn_config.cipher_key = os.getenv("PN_CIPHER_KEY")

        self.pubnub = PubNub(pn_config)
        self.model = ActivityModel()

    def process_command(self, data):
        self.model.log_event(data)

        envelope = self.pubnub.publish().channel("light_control").message(data).sync()

        return not envelope.status.is_error()
