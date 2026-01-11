from pymongo import MongoClient
import datetime
import os

class ActivityModel:
    def __init__(self):
        client = MongoClient(os.getenv("MONGO_URI"))
        self.db = client[os.getenv("MONGO_DB_NAME")]
        self.collection = self.db['activity_logs']

    def log_event(self, data):
        log_entry = {
            "timestamp": datetime.datetime.utcnow(),
            "mode": data.get('mode'),
            "brightness": data.get('brightness'),
            "power": data.get('power'),
            "source": "web_dashboard"
        }
        return self.collection.insert_one(log_entry)