from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from models.activity import ActivityModel
import os


class LightController:
    def __init__(self):
        pn_config = PNConfiguration()
        pn_config.publish_key = os.getenv("PN_PUB_KEY")
        pn_config.subscribe_key = os.getenv("PN_SUB_KEY")
        pn_config.secret_key = os.getenv("PN_SEC_KEY")  # Чтобы publish прошел через PAM
        pn_config.user_id = "aws_backend_controller"
        pn_config.secure = True

        self.pubnub = PubNub(pn_config)
        self.model = ActivityModel()

    def process_command(self, data):
        # Логируем в Mongo (пароль из MONGO_URI)
        try:
            self.model.log_event(data)
        except Exception as e:
            print(f"DB Error: {e}")

        channel = os.getenv("PUBNUB_CONTROL_CHANNEL")
        envelope = self.pubnub.publish().channel(channel).message(data).sync()

        if envelope.status.is_error():
            print(f"PubNub Error: {envelope.status.error_data}")

        return not envelope.status.is_error()