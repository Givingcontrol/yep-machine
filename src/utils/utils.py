import asyncio

import pigpio

import config
from utils.run_moves import RunMoves


class Utils(RunMoves):
    def __init__(self, hardware):
        self.hardware = hardware
        self.pi = hardware.pi
        super(Utils, self).__init__(self, hardware)

    def create_wave(self, period):
        period = int(period * 1000000)  # convert s to ns
        wave = [
            pigpio.pulse(1 << config.PULSE_PIN, 0, period),
            pigpio.pulse(0, 1 << config.PULSE_PIN, period),
        ]
        self.pi.wave_add_generic(wave)
        return self.pi.wave_create()

    async def move(self, steps):
        self.pi.wave_clear()
        wave_id = self.create_wave(0.0005)

        # generate number of steps per frequency
        steps_number_below_256 = steps & 255
        steps_number_times_256 = steps >> 8

        chain = [255, 0, wave_id, 255, 1, steps_number_below_256,
                 steps_number_times_256]

        self.pi.wave_chain(chain)  # Transmit chain.

        while self.pi.wave_tx_busy():  # While transmitting.
            await asyncio.sleep(0.01)

        # delete all waves
        self.pi.wave_delete(0)
