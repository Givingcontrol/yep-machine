import json

import pigpio

import config
from streams import status


async def stop(pi, status_ws):
    pi.set_mode(config.PULSE_PIN, pigpio.INPUT)
    await status_ws.send(
        json.dumps(dict(stream=status.status, device="machine", type=status.waiting))
    )
