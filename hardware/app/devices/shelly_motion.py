import time
from bleak import BleakScanner
from hardware.app.config import SHELLY_NAME

last_motion_ts = 0


def ble_callback(device, adv):
    global last_motion_ts
    if device.name == SHELLY_NAME:
        last_motion_ts = time.time()
        print(f"🟢 MOTION from {device.address}")


class ShellyMotion:
    def __init__(self):
        self.scanner = BleakScanner(ble_callback)

    async def start(self):
        await self.scanner.start()

    async def stop(self):
        await self.scanner.stop()
