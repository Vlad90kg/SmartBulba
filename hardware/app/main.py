import asyncio
import time

from hardware.app.devices.tapo_bulb import discover_bulb
from hardware.app.devices.shelly_motion import ShellyMotion, last_motion_ts
from hardware.app.config import MOTION_TIMEOUT, BRIGHTNESS


async def main():
    bulb = await discover_bulb()
    if not bulb:
        print("Tapo bulb not found")
        return

    sensor = ShellyMotion()
    await sensor.start()

    print(" Motion → Light active")
    light_on = False

    try:
        while True:
            now = time.time()
            import hardware.app.devices.shelly_motion as sensor_module

            motion_delta = now - sensor_module.last_motion_ts

            if sensor_module.last_motion_ts > 0 and motion_delta < MOTION_TIMEOUT:
                if not light_on:
                    print(f"--- Motion detected {motion_delta:.2f} sec. ago ---")
                    await bulb.on(BRIGHTNESS)
                    light_on = True
                    print("💡LIGHT ON")
            else:
                if light_on:
                    print(f"--- No motion {motion_delta:.2f} sec. ---")
                    await bulb.off()
                    light_on = False
                    print(" LIGHT OFF")
            await asyncio.sleep(0.5)
    finally:
        await sensor.stop()


if __name__ == "__main__":
    asyncio.run(main())

