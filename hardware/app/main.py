import asyncio
from hardware.app.devices.tapo_bulb import TapoBulb
from hardware.app.devices.shelly_motion import ShellyMotion
from hardware.app.rules.motion_rule import handle_motion
from hardware.app.state import state


async def main():
    bulb = TapoBulb()
    sensor = ShellyMotion()

    await sensor.start()
    print("Hardware layer running")

    try:
        while True:
            await handle_motion(state, bulb)
            await asyncio.sleep(1)
    finally:
        await sensor.stop()

asyncio.run(main())
