import json
from exceptions import Malfunction

from context.utils import Utils
from streams import status


class LoopWave:
    def __init__(self, context):
        self.hardware = context.hardware
        self.pi = context.pi
        self.ws = context.ws
        self.utils = context.utils

    async def run(self, data):
        # todo: measure and log one loop execution time
        await self.ws.send(
            json.dumps(
                {"stream": status.status, "device": "machine", "type": status.running}
            )
        )
        if self.hardware.limit_pressed:
            raise Malfunction("Limit switch pressed at the start of loop_wave")

        while True:
            await self.utils.run_moves(data)
            await self.utils.compensate_for_steps()
