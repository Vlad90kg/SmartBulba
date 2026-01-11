import time
from bleak import BleakScanner
from hardware.app.config import SHELLY_NAME



class ShellyMotion:
    def __init__(self):
        self.scanner = None
        self.last_motion_ts = 0

    def _callback(self, device, adv):
        if device.name and SHELLY_NAME in device.name:
            self.last_motion_ts = time.time()
            print(f"MOTION from {device.name}")

    async def start(self):
        print(f" Scanning for {SHELLY_NAME}...")
        self.scanner = BleakScanner(self._callback)
        await self.scanner.start()

    async def stop(self):
        if self.scanner:
            await self.scanner.stop()

