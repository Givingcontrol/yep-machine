import asyncio
import json
from commands.calibrate import calibrate
from commands.loop_wave import loop_wave
from commands.stop import stop

import pigpio
import websockets

import config
from streams import commands

pi = pigpio.pi()
pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)
pi.wave_tx_stop()
pi.wave_clear()

HANDLERS = {
    commands.stop: stop,
    commands.calibrate: calibrate,
    commands.loop_wave: loop_wave,
}

LOCKING_COMMANDS = (commands.loop_wave, commands.calibrate)

loop_ = asyncio.new_event_loop()


class Run:
    def __init__(self):
        self.locking_task = None

    async def run_handler(self, message, ws):
        try:
            data = message.get("data")
            if data:
                await HANDLERS[message["type"]](pi, ws, json.loads(data))
            else:
                await HANDLERS[message["type"]](pi, ws)
        except Exception as exception:
            pi.set_mode(config.PULSE_PIN, pigpio.INPUT)
            pi.wave_tx_stop()
            pi.wave_clear()
            print("Command exception:", exception)

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
                        pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
                        pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)


runner = Run()

asyncio.get_event_loop().run_until_complete(runner.loop())
pi.stop()
