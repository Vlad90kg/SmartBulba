import asyncio
import time
import os

from dotenv import load_dotenv
from kasa import Discover
from hardware.app.config import MOTION_TIMEOUT, BRIGHTNESS
from hardware.app.devices.shelly_motion import ShellyMotion, last_motion_ts
from hardware.app.devices.tapo_bulb import TapoBulb

load_dotenv()

TAPO_USER = os.getenv("TAPO_USERNAME")
TAPO_PASS = os.getenv("TAPO_PASSWORD")


async def discover_bulb():
    devices = await Discover.discover(
        username=TAPO_USER,
        password=TAPO_PASS,
    )
    for dev in devices.values():
        if dev.model == "L530E":
            await dev.update()
            print("✅ Bulb discovered")
            return TapoBulb(dev)
    return None


async def main():
    bulb = await discover_bulb()
    if not bulb:
        print("❌ Bulb not found")
        return

    sensor = ShellyMotion()
    await sensor.start()

    light_on = False
    print("🚀 Motion → Light active")

    try:
        while True:
            now = time.time()

            if now - last_motion_ts < MOTION_TIMEOUT:
                if not light_on:
                    await bulb.on(BRIGHTNESS)
                    light_on = True
                    print("💡 LIGHT ON")
            else:
                if light_on:
                    await bulb.off()
                    light_on = False
                    print("🌑 LIGHT OFF")

            await asyncio.sleep(1)

    finally:
        await sensor.stop()


if __name__ == "__main__":
    asyncio.run(main())
