import json

from streams import status
from utils.exceptions import Malfunction
from utils.run_movements import run_movements


class LoopWave:
    def __init__(self, hardware, ws):
        self.hardware = hardware
        self.pi = hardware.pi
        self.ws = ws

    async def run(self, data):
        # todo: measure and log one loop execution time
        await self.ws.send(
            json.dumps(
                {"stream": status.status, "device": "machine", "type": status.running}
            )
        )
        if self.hardware.limit_pressed:
            raise Malfunction('Limit switch pressed at the start of loop_wave')

        while True:
            await run_movements(self.pi, data)
