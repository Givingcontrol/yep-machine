from common.run_movements import run_movements


async def loop_wave(status_ws, data):
    while True:
        await run_movements(data)
