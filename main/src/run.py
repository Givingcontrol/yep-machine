import asyncio
import json
import time
import traceback

import pigpio
import websockets

import config
from commands.calibrate import Calibrate
from commands.loop_wave import LoopWave
from commands.stop import Stop
from context.context import Context
from exceptions import Malfunction
from streams import commands


class Run:
    def __init__(self):
        self.context = Context()
        self.hardware = self.context.hardware
        self.pi = self.context.pi
        self.settings = self.context.settings

        self.locking_task = None
        self.queue = asyncio.Queue()

        self.handlers = {
            "stop": {"class": Stop, "interrupting": True},
            "calibrate": {"class": Calibrate, "persistent": True},
            "loop_wave": {"class": LoopWave, "persistent": True},
            "update_settings": {
                "function": self.settings.update_settings,
                # "locking": True
            },
        }

    async def run_handler(self, message):
        message_time = message["time"]
        print((time.time() - float(message_time)) * 1000, "ms delay")
        try:
            handler = self.handlers[message["type"]]
            if handler.get("class"):
                await self.handle_class(handler, message)
            elif handler.get("function"):
                handler.get("function")()

        except Malfunction as exception:
            self.hardware.reset(exception)
        except Exception as e:
            print(traceback.format_exc())

    async def handle_class(self, handler, message):
        handler = handler["class"](self.context)
        data = message.get("data")
        if data:
            await handler.run(json.loads(data))
        else:
            await handler.run()

    async def loop(self):
        self.context.ws = await websockets.connect(
            config.WS_URL + commands.command_all, ping_interval=5
        )
        while True:
            try:
                messages = await self.context.ws.recv()
            except websockets.ConnectionClosedError:
                print("Connection closed, waiting")
                await asyncio.sleep(1)
                self.context.ws = await websockets.connect(
                    config.WS_URL + commands.command_all, ping_interval=5
                )
            else:
                messages = json.loads(messages)
                for message in messages:
                    print("Command ", message["type"])
                    handler = self.handlers[message["type"]]
                    if handler.get("interrupting") and self.locking_task:
                        self.locking_task.cancel()

                    self.hardware.reset("cleanup")
                    task = asyncio.create_task(self.run_handler(message))

                    if handler.get("persistent"):
                        if self.locking_task:
                            self.locking_task.cancel()
                        self.locking_task = task
                        self.pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
                        self.pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)


runner = Run()

asyncio.get_event_loop().run_until_complete(runner.loop())
