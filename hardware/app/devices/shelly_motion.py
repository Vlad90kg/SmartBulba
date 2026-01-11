import time
from bleak import BleakScanner
from hardware.app.config import SHELLY_NAME

last_motion_ts = 0

def register_motion(device_name: str):
    global last_motion_ts
    last_motion_ts = time.time()
    print(f"MOTION from {device_name}")

class ShellyMotion:
    def __init__(self):
        self.scanner = None

    def _callback(self, device, adv):
        if device.name and SHELLY_NAME in device.name:
            register_motion(device.name)

    async def start(self):
        self.scanner = BleakScanner(self._callback)
        await self.scanner.start()

    async def stop(self):
        if self.scanner:
            await self.scanner.stop()

