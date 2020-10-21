import json

from common.run_movements import run_movements
from streams import status


async def loop_wave(status_ws, data):
    await status_ws.send(
        json.dumps({"stream": status.status, "device": "machine", "type": status.running})
    )
    while True:
        await run_movements(data)
