import asyncio
from logging import getLogger
from kasa import Discover
from hardware.app.config import TAPO_USERNAME, TAPO_PASSWORD

logger = getLogger("TapoBulb")


class TapoBulb:
    def __init__(self):
        self.device = None
        self.connected = False

    async def connect(self, retries=5, delay=3):
        if self.connected:
            return

        for _ in range(retries):
            devices = await Discover.discover(
                username=TAPO_USERNAME,
                password=TAPO_PASSWORD
            )

            for dev in devices.values():
                if dev.model == "L530E":
                    await dev.update()
                    self.device = dev
                    self.connected = True
                    logger.info("Connected to Tapo L530E")
                    return

            await asyncio.sleep(delay)

        raise RuntimeError("Tapo L530E not found")

    async def on(self, brightness: int):
        await self.connect()
        await self.device.modules["Light"].set_brightness(brightness)
        await self.device.modules["Light"].turn_on()
        logger.info("Bulb ON (%s)", brightness)

    async def off(self):
        await self.connect()
        await self.device.modules["Light"].turn_off()
        logger.info("Bulb OFF")
