import time
from hardware.app.config import MOTION_TIMEOUT, BRIGHTNESS_MAP

_last_motion_ts = 0


def register_motion():
    global _last_motion_ts
    _last_motion_ts = time.time()


async def handle_motion(state, bulb):
    if state.mode != "motion":
        return

    now = time.time()

    if now - _last_motion_ts < MOTION_TIMEOUT:
        if not state.power:
            await bulb.on(BRIGHTNESS_MAP[state.brightness])
            state.power = True
    else:
        if state.power:
            await bulb.off()
            state.power = False
