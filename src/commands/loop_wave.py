import json

from streams import status
from utils.run_movements import run_movements


async def loop_wave(pi, status_ws, data):
    await status_ws.send(
        json.dumps(
            {"stream": status.status, "device": "machine", "type": status.running}
        )
    )
    while True:
        await run_movements(pi, data)
