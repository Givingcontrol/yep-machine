import json

import pigpio

import config
from streams import status


class Stop:
    def __init__(self, hardware, ws):
        self.hardware = hardware
        self.pi = hardware.pi
        self.ws = ws

    async def run(self):
        self.pi.set_mode(config.PULSE_PIN, pigpio.INPUT)
        await self.ws.send(
            json.dumps(
                dict(stream=status.status, device="machine", type=status.waiting)
            )
        )
