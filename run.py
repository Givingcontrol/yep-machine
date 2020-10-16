import json
import threading

import pigpio
import config
import asyncio
import websockets
from streams import commands, status

from commands.stop import stop
from commands.calibrate import calibrate
from commands.loop_wave import loop_wave

pi = pigpio.pi()
pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)

HANDLERS = {
    commands.stop: stop,
    commands.calibrate: calibrate,
    commands.loop_wave: loop_wave
}

LOCKING_COMMANDS = (commands.loop_wave, commands.calibrate)

loop_ = asyncio.new_event_loop()


class Run:
    def __init__(self):
        self.locking_thread = None

    async def run_handler(self, message, status_ws):
        data = message.get('data')
        if data:
            await HANDLERS[message['type']](status_ws, json.loads(data))
        else:
            await HANDLERS[message['type']](status_ws)

    async def loop(self):
        status_ws = await websockets.connect(config.WS_URL + status.status)

        async with websockets.connect(config.WS_URL + commands.command_all) as websocket:
            while True:
                messages = await websocket.recv()
                messages = json.loads(messages)
                for message in messages:
                    message_type = message['type']
                    print(message_type)
                    if message_type == 'stop' and self.locking_thread:
                        self.locking_thread.cancel()
                    self.locking_thread = asyncio.create_task(self.run_handler(message, status_ws))
             
                    if message_type in LOCKING_COMMANDS:
                        pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
                        pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)


runner = Run()

asyncio.get_event_loop().run_until_complete(runner.loop())
pi.stop()
