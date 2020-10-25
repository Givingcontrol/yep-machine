import asyncio
import json

import pigpio

import config
from streams import status
from utils.exceptions import Malfunction
from utils.wave import create_wave


class Calibrate:
    def __init__(self, hardware, ws):
        self.hardware = hardware
        self.pi = hardware.pi
        self.ws = ws

    async def run(self):
        self.hardware.disable_limit_monitoring()
        
        await self.ws.send(
            json.dumps(
                {"stream": status.status, "device": "machine", "type": status.running}
            )
        )
        # todo: increase calibration speed, first multiple steps per check, then finer adjustments
        self.pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
        self.pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)
        self.pi.wave_clear()

        wave = create_wave(self.pi, 0.01)
        # go to the back
        self.pi.write(config.DIRECTION_PIN, False)
        while not self.hardware.back_limit.is_pressed:
            if self.hardware.front_limit.is_pressed:
                raise Malfunction("Wrong direction")

            await asyncio.sleep(0)
            if not self.pi.wave_tx_busy():
                # todo: check why WAVE_MODE_ONE_SHOT_SYNC queues too many waves that keep running
                self.pi.wave_send_using_mode(wave, pigpio.WAVE_MODE_ONE_SHOT)

        # go to the front while counting steps
        self.pi.write(config.DIRECTION_PIN, True)
        steps_counter = 0
        while not self.hardware.front_limit.is_pressed:
            if steps_counter > 10 and self.hardware.back_limit.is_pressed:
                raise Malfunction("Wrong direction")

            await asyncio.sleep(0)
            if not self.pi.wave_tx_busy():
                steps_counter += 1
                self.pi.wave_send_using_mode(wave, pigpio.WAVE_MODE_ONE_SHOT)

        print(steps_counter)
        self.hardware.position = steps_counter

        self.pi.wave_tx_stop()
        self.pi.wave_clear()

        self.hardware.enable_limit_monitoring()