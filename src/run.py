import asyncio
import json

from commands.calibrate import Calibrate
from commands.loop_wave import LoopWave
from commands.stop import Stop

import pigpio
import websockets

import config
from hardware import Hardware
from streams import commands
from exceptions import Malfunction

HANDLERS = {
    commands.stop: Stop,
    commands.calibrate: Calibrate,
    commands.loop_wave: LoopWave,
}

LOCKING_COMMANDS = (commands.loop_wave, commands.calibrate)


class Run:
    def __init__(self):
        self.locking_task = None
        self.hardware = Hardware()
        self.pi = self.hardware.pi

    async def run_handler(self, message, ws):
        try:
            data = message.get("data")
            handler = HANDLERS[message["type"]](self.hardware, ws)
            if data:
                await handler.run(json.loads(data))
            else:
                await handler.run()
        except Malfunction as exception:
            self.hardware.reset(exception)

    async def loop(self):
        async with websockets.connect(
                config.WS_URL + commands.command_all, ping_interval=5
        ) as websocket:
            while True:
                messages = await websocket.recv()
                messages = json.loads(messages)
                for message in messages:
                    message_type = message["type"]
                    print(message_type)
                    if message_type == "stop" and self.locking_task:
                        self.locking_task.cancel()

                    task = asyncio.create_task(self.run_handler(message, websocket))

                    if message_type in LOCKING_COMMANDS:
                        if self.locking_task:
                            self.locking_task.cancel()
                        self.locking_task = task
                        self.pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
                        self.pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)


runner = Run()

asyncio.get_event_loop().run_until_complete(runner.loop())
