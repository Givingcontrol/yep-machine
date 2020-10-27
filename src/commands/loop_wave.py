import json
from exceptions import Malfunction

from streams import status
from utils import Utils


class LoopWave:
    def __init__(self, hardware, ws):
        self.hardware = hardware
        self.pi = hardware.pi
        self.ws = ws
        self.utils = Utils(hardware)

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
            await self.hardware.compensate_for_steps()
