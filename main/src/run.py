import asyncio
import json
import time
import traceback

import pigpio
import websockets

import config
from commands.calibrate import Calibrate
from commands.end import End
from commands.loop_wave import LoopWave
from commands.stop import Stop
from commands.update_settings import UpdateSettings
from context.context import Context
from exceptions import Malfunction
from streams import commands

# ordered from highest to lowest priority
QUEUED_COMMANDS = ["update_settings", "calibrate", "loop_wave"]


class Run:
    def __init__(self):
        self.context = Context()
        self.hardware = self.context.hardware
        self.pi = self.context.pi
        self.settings = self.context.settings

        self.locking_task = None
        self.queue = asyncio.Queue()

        self.handlers = {
            "stop": {"class": Stop},
            "end": {"class": End},
            "calibrate": {"class": Calibrate, "persistent": True},
            "loop_wave": {"class": LoopWave, "persistent": True},
            "update_settings": {"class": UpdateSettings, "persistent": True},
        }
        self.tasks_queue = {key: None for key in QUEUED_COMMANDS}

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
        self.locking_task = None
        await self.run_queue()

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
                    command = message["type"]
                    print("Command ", command)

                    if message["type"] == "stop" and self.locking_task:
                        self.locking_task.cancel()
                        self.locking_task = None
                        self.hardware.reset("STOP command")

                    if command in QUEUED_COMMANDS:
                        self.hardware.end = True
                        self.tasks_queue[command] = message
                        # clear lower priority tasks to allow them to run only from highest to lowest priority
                        command_index = QUEUED_COMMANDS.index(command)
                        for index, item in enumerate(QUEUED_COMMANDS):
                            if index > command_index:
                                self.tasks_queue[item] = None
                    else:
                        asyncio.create_task(self.run_handler(message))
            await self.run_queue()

    async def run_queue(self):
        if not self.locking_task:
            for key in QUEUED_COMMANDS:
                message = self.tasks_queue.get(key)
                if message:
                    self.tasks_queue[key] = None
                    task = asyncio.create_task(self.run_handler(message))
                    self.locking_task = task
                    break


runner = Run()

asyncio.get_event_loop().run_until_complete(runner.loop())
