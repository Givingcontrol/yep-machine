import json

import pigpio

import config
from streams import status


class End:  # todo: implement
    def __init__(self, context):
        self.hardware = context.hardware
        self.pi = context.pi
        self.ws = context.ws

    async def run(self):
        self.pi.set_mode(config.PULSE_PIN, pigpio.INPUT)
        # self.hardware.reset("stopped")
        await self.ws.send(
            json.dumps(
                dict(stream=status.status, device="machine", type=status.waiting)
            )
        )
