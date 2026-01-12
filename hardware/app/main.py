import asyncio
import time
import os
import sys
from bleak import BleakScanner
from dotenv import load_dotenv

try:
    from hardware.app.devices.tapo_bulb import discover_bulb
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

load_dotenv()

TARGET_MAC = "B0:C7:DE:32:3E:74"
MY_TIMEOUT = 120
last_packet_time = time.time()
last_motion_ts = 0
light_on = False


def ble_callback(device, adv):
    global last_motion_ts, last_packet_time
    if device.address.upper() == TARGET_MAC:
        last_packet_time = time.time()
        ts = time.strftime('%H:%M:%S')

        bthome_uuid = "0000fcd2-0000-1000-8000-00805f9b34fb"
        data = adv.service_data.get(bthome_uuid)

        if data:
            payload = data.hex()
            if "2101" in payload:
                last_motion_ts = time.time()
                print(f" [{ts}] MOTION | RSSI: {adv.rssi}")
            else:
                print(f" [{ts}] KEEP-ALIVE | RSSI: {adv.rssi}")


async def main():
    global last_motion_ts, last_packet_time, light_on

    print(" Discovering bulb...")
    bulb = await discover_bulb()
    if bulb:
        print(f"✅ Bulb connected. Monitoring {TARGET_MAC}")
    else:
        print(" Bulb not found. Observation mode only.")

    while True:
        # Re-initializing scanner to prevent driver stalls
        scanner = BleakScanner(ble_callback, scanning_mode="active")
        await scanner.start()

        try:
            for _ in range(30):
                now = time.time()
                diff = now - last_motion_ts if last_motion_ts > 0 else 999999

                if diff < MY_TIMEOUT:
                    if not light_on:
                        print("💡 LIGHT ON")
                        if bulb: asyncio.create_task(bulb.on(100))
                        light_on = True
                else:
                    if light_on:
                        print("🌑 LIGHT OFF (Timeout)")
                        if bulb: asyncio.create_task(bulb.off())
                        light_on = False

                await asyncio.sleep(1)

            if time.time() - last_packet_time > 60:
                print(f"⏳ Waiting for sensor... ({int(time.time() - last_packet_time)}s silence)")

        except Exception as e:
            print(f"💥 Runtime Error: {e}")
        finally:
            await scanner.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTerminated.")
    except Exception as e:
        print(f" Critical Failure: {e}")
