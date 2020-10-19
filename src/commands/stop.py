import json

import config
import pigpio
from streams import status

pi = pigpio.pi()


async def stop(status_ws):
    pi.set_mode(config.PULSE_PIN, pigpio.INPUT)
    await status_ws.send(
        json.dumps(dict(stream=status.status, device="machine", type=status.waiting))
    )
    print("SENT WAITING")
