import asyncio
import json

import pigpio
import requests

import config
from exceptions import Malfunction
from streams import status


class Calibrate:
    def __init__(self, context):
        self.hardware = context.hardware
        self.pi = context.pi
        self.ws = context.ws
        self.utils = context.utils
        self.settings = context.settings
        self.hardware.enable_limit_monitoring()

    async def run(self):
        self.hardware.disable_limit_monitoring()

        await self.ws.send(
            json.dumps(
                {"stream": status.status, "device": "machine", "type": status.running}
            )
        )
        self.pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
        self.pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)
        self.pi.wave_clear()

        # go to the front
        forward_wave = self.utils.create_wave(0.00005)
        self.pi.write(config.DIRECTION_PIN, True)
        while not self.hardware.front_limit.is_pressed:
            if self.hardware.back_limit.is_pressed:
                raise Malfunction("Back limit pressed while moving forward")

            await asyncio.sleep(0)
            if not self.pi.wave_tx_busy():
                # todo: check why WAVE_MODE_ONE_SHOT_SYNC queues too many waves that keep running
                self.pi.wave_send_using_mode(forward_wave, pigpio.WAVE_MODE_ONE_SHOT)

        # todo: count since switch release instead of press, slow moves until release
        # go to the back while counting steps
        backward_wave = self.utils.create_wave(0.00004)
        self.pi.write(config.DIRECTION_PIN, False)
        steps_counter = 0
        while not self.hardware.back_limit.is_pressed:
            if steps_counter > 500 and self.hardware.front_limit.is_pressed:
                raise Malfunction("Front limit pressed while moving backward")
            await asyncio.sleep(0)
            if not self.pi.wave_tx_busy():
                steps_counter += 1
                print(steps_counter)
                self.pi.wave_send_using_mode(backward_wave, pigpio.WAVE_MODE_ONE_SHOT)

        await self.utils.move(self.settings.padding_steps, True)

        self.hardware.position = 0
        response = requests.put(
            f"{config.API_URL}settings/machine-thrust/default/",
            json.dumps({"max_steps": steps_counter - self.settings.padding_steps * 2}),
        )
        print("sc", steps_counter)
        self.settings.set_settings(response.json())

        self.pi.wave_tx_stop()
        self.pi.wave_clear()

        self.hardware.enable_limit_monitoring()
