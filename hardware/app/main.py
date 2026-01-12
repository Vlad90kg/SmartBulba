import asyncio
import time
import os
import sys
from bleak import BleakScanner
from dotenv import load_dotenv
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_asyncio import PubNubAsyncio

try:
    from hardware.app.devices.tapo_bulb import discover_bulb
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

load_dotenv()

TARGET_MAC = os.getenv("SHELLY_MAC", "B0:C7:DE:32:3E:74")
MY_TIMEOUT = int(os.getenv("MOTION_TIMEOUT", 30))
CONTROL_CHANNEL = os.getenv("PUBNUB_CONTROL_CHANNEL", "light_control")

BRIGHTNESS_MAP = {
    "low": 30,
    "medium": 60,
    "high": 100
}

last_packet_time = time.time()
last_motion_ts = 0
light_on = False
system_mode = "motion"
current_brightness = 100
bulb = None


class ControlListener(SubscribeCallback):
    def message(self, pubnub, message):
        global system_mode, light_on, current_brightness
        data = message.message
        print(f"Remote command received: {data}")

        system_mode = data.get("mode", "motion")
        bright_key = data.get("brightness", "high")
        current_brightness = BRIGHTNESS_MAP.get(bright_key, 100)
        power_cmd = data.get("power")

        if system_mode == "manual" and bulb:
            if power_cmd is True:
                print(f"Manual mode: Set ON (Brightness: {current_brightness}%)")
                asyncio.create_task(bulb.on(current_brightness))
                light_on = True
            else:
                print("Manual mode: Set OFF")
                asyncio.create_task(bulb.off())
                light_on = False


def ble_callback(device, adv):
    global last_motion_ts, last_packet_time
    if device.address.upper() == TARGET_MAC:
        last_packet_time = time.time()
        ts = time.strftime('%H:%M:%S')
        bthome_uuid = "0000fcd2-0000-1000-8000-00805f9b34fb"
        data = adv.service_data.get(bthome_uuid)
        if data and "2101" in data.hex():
            last_motion_ts = time.time()
            print(f"[{ts}] Motion event detected")


async def main():
    global last_motion_ts, last_packet_time, light_on, bulb

    pnconfig = PNConfiguration()
    pnconfig.publish_key = os.getenv("PUBNUB_PUB_KEY")
    pnconfig.subscribe_key = os.getenv("PUBNUB_SUB_KEY")
    pnconfig.user_id = "raspberry_pi_main"

    pub_instance = PubNubAsyncio(pnconfig)
    pub_instance.add_listener(ControlListener())
    pub_instance.subscribe().channels(CONTROL_CHANNEL).execute()

    print("Status: Discovering bulb...")
    bulb = await discover_bulb()
    if bulb:
        print(f"Status: Bulb connected. Monitoring {TARGET_MAC}")

    while True:
        scanner = BleakScanner(ble_callback, scanning_mode="active")
        await scanner.start()
        try:
            for _ in range(30):
                now = time.time()
                if system_mode == "motion":
                    diff = now - last_motion_ts if last_motion_ts > 0 else 999999
                    if diff < MY_TIMEOUT:
                        if not light_on:
                            print(f"Action: Auto ON ({current_brightness}%)")
                            if bulb: asyncio.create_task(bulb.on(current_brightness))
                            light_on = True
                    else:
                        if light_on:
                            print("Action: Auto OFF (Timeout)")
                            if bulb: asyncio.create_task(bulb.off())
                            light_on = False
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await scanner.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStatus: Terminated")