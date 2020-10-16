import json

import pigpio

import config
from streams import status

pi = pigpio.pi()


async def stop(status_ws):
    print('stop', status_ws)
    pi.set_mode(config.PULSE_PIN, pigpio.INPUT)
    await status_ws.send(json.dumps({"type": status.waiting}))
