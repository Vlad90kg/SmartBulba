from bleak import BleakScanner
from hardware.app.config import SHELLY_MAC
from hardware.app.rules.motion_rule import register_motion


class ShellyMotion:
    def __init__(self):
        self.scanner = None

    def _callback(self, device, adv):
        if device.address.upper() == SHELLY_MAC:
            register_motion()

    async def start(self):
        self.scanner = BleakScanner(self._callback)
        await self.scanner.start()

    async def stop(self):
        await self.scanner.stop()
