import os
import asyncio
from kasa import Discover
from dotenv import load_dotenv

load_dotenv()

TAPO_USER = os.getenv("TAPO_USERNAME")
TAPO_PASS = os.getenv("TAPO_PASSWORD")
TAPO_MODEL = "L530E"

class TapoBulb:
    def __init__(self, device):
        self.device = device

    async def on(self, brightness: int):
        try:
            await self.device.update() 
            await self.device.set_brightness(brightness)
            await self.device.turn_on()
            await self.device.update() 
            print(f"✅ Hardware Command Sent: On at {brightness}%")
        except Exception as e:
            print(f"Tapo Hardware Error: {e}")

    async def off(self):
        try:
            await self.device.turn_off()
            await self.device.update()
            print("✅ Hardware Command Sent: Off")
        except Exception as e:
            print(f"Tapo Hardware Error: {e}")


async def discover_bulb(retries=5, delay=3):
    for attempt in range(1, retries + 1):
        print(f"Discovering Tapo bulb (attempt {attempt})...")
        try:
            devices = await Discover.discover(
                username=TAPO_USER,
                password=TAPO_PASS
            )

            for dev in devices.values():
                if dev.model == TAPO_MODEL:
                    await dev.update()
                    print(f"Bulb discovered at {dev.host}")
                    return TapoBulb(dev)
        except Exception as e:
            print(f"Discovery error: {e}")

        await asyncio.sleep(delay)

    return None
