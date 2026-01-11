import time
import asyncio
from collections import deque
from bleak import BleakScanner
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from dotenv import load_dotenv
import os
import statistics

# ---------- CONFIG ----------
load_dotenv()

SHELLY_NAME = os.getenv("SHELLY_NAME", "Shelly")
CHANNEL = os.getenv("PUBNUB_ACTIVITY_CHANNEL")

WINDOW_SECONDS = 5.0
ACTIVE_THRESHOLD = 0.7
IDLE_THRESHOLD = 0.3

# ---------- PUBNUB ----------
pnconfig = PNConfiguration()
pnconfig.publish_key = os.getenv("PUBNUB_PUB_KEY")
pnconfig.subscribe_key = os.getenv("PUBNUB_SUB_KEY")
pnconfig.uuid = os.getenv("PUBNUB_UUID", "edge-agent")
pubnub = PubNub(pnconfig)

# ---------- STATE ----------
events = deque()  # (timestamp, rssi)
current_state = "EMPTY"

# ---------- BLE CALLBACK ----------
def ble_callback(device, adv):
    if device.name and SHELLY_NAME in device.name:
        now = time.time()
        rssi = device.rssi
        events.append((now, rssi))

# ---------- ACTIVITY SCORE ----------
def compute_activity():
    now = time.time()
    # cleanup old events
    while events and now - events[0][0] > WINDOW_SECONDS:
        events.popleft()

    if not events:
        return 0.0

    packet_rate = len(events) / WINDOW_SECONDS

    rssi_values = [r for _, r in events]
    rssi_variance = statistics.pvariance(rssi_values) if len(rssi_values) > 1 else 0

    rate_score = min(packet_rate / 6.0, 1.0)
    rssi_score = min(rssi_variance / 20.0, 1.0)

    return round((rate_score * 0.7 + rssi_score * 0.3), 2)

# ---------- STATE MACHINE ----------
def classify_state(score):
    if score >= ACTIVE_THRESHOLD:
        return "ACTIVE"
    if score >= IDLE_THRESHOLD:
        return "IDLE"
    return "EMPTY"

# ---------- MAIN LOOP ----------
async def main():
    global current_state

    print("🔵 Starting BLE activity agent...")
    scanner = BleakScanner(ble_callback)
    await scanner.start()

    try:
        while True:
            score = compute_activity()
            new_state = classify_state(score)
            if new_state != current_state:
                current_state = new_state

                payload = {
                    "state": current_state,
                    "activity_score": score,
                    "timestamp": int(time.time())
                }

                pubnub.publish().channel(CHANNEL).message(payload).sync()
                print("📡 Published:", payload)

            await asyncio.sleep(1)

    finally:
        await scanner.stop()

if __name__ == "__main__":
    asyncio.run(main())


