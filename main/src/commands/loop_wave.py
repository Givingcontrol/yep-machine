import json

from exceptions import Malfunction
from streams import status


class LoopWave:
    def __init__(self, context):
        self.hardware = context.hardware
        self.ws = context.ws
        self.utils = context.utils

    async def run(self, data):
        # todo: measure and log one loop execution time
        # todo: check if in position 0
        self.hardware.end = False
        await self.ws.send(
            json.dumps(
                {"stream": status.status, "device": "machine", "type": status.running}
            )
        )
        if self.hardware.limit_pressed:
            raise Malfunction("Limit switch pressed at the start of loop_wave")

        await self.utils.run_moves(data)
