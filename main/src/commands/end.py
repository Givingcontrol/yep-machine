import json

import pigpio

import config
from streams import status


class End:
    def __init__(self, context):
        self.hardware = context.hardware
        self.ws = context.ws

    async def run(self):
        self.hardware.end = True

    async def handle_end(self):
        await self.ws.send(
            json.dumps(
                dict(stream=status.status, device="machine", type=status.waiting)
            )
        )
        self.hardware.end = False
        for handler in self.hardware.post_end:
            prin
            handler()
        self.hardware.post_end = []
