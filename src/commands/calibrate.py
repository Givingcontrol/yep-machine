import asyncio
import json

import pigpio

import config
from streams import status
from exceptions import Malfunction
from utils import Utils


class Calibrate:
    def __init__(self, hardware, ws):
        self.hardware = hardware
        self.pi = hardware.pi
        self.ws = ws
        self.utils = Utils(hardware)

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
        forward_wave = self.utils.create_wave(0.0005)
        self.pi.write(config.DIRECTION_PIN, True)
        while not self.hardware.front_limit.is_pressed:
            if self.hardware.back_limit.is_pressed:
                raise Malfunction("Wrong direction")

            await asyncio.sleep(0)
            if not self.pi.wave_tx_busy():
                # todo: check why WAVE_MODE_ONE_SHOT_SYNC queues too many waves that keep running
                self.pi.wave_send_using_mode(forward_wave, pigpio.WAVE_MODE_ONE_SHOT)

        # go to the front while counting steps
        # todo: count since switch release instead of press, slow moves until release
        backward_wave = self.utils.create_wave(0.0004)
        self.pi.write(config.DIRECTION_PIN, False)
        steps_counter = 0
        while not self.hardware.back_limit.is_pressed:
            if steps_counter > 50 and self.hardware.front_limit.is_pressed:
                raise Malfunction("Wrong direction")

            await asyncio.sleep(0)
            if not self.pi.wave_tx_busy():
                steps_counter += 1
                self.pi.wave_send_using_mode(backward_wave, pigpio.WAVE_MODE_ONE_SHOT)

        self.pi.write(config.DIRECTION_PIN, True)
        # todo: set position to 0 on first step after releasing, move steps from there
        await self.utils.move(config.PADDING_STEPS)

        self.hardware.position = 0
        self.hardware.max_position = steps_counter - config.PADDING_STEPS

        self.pi.wave_tx_stop()
        self.pi.wave_clear()

        self.hardware.enable_limit_monitoring()
