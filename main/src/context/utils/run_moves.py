import asyncio
import time

import pigpio

import config
from i2c.arduino import device


class RunMoves:
    def __init__(self, utils, hardware, settings):
        self.hardware = hardware
        self.pi = hardware.pi
        self.utils = utils
        self.settings = settings

    async def _generate_ramp(self, steps):
        self.pi.wave_clear()
        wave_ids = [-1] * len(steps)

        # generate wave period
        for index, step in enumerate(steps):
            # todo: fix timing, not quite per second, more like per 1.5 seconds
            frequency = step * self.settings.wave_resolution * 2
            if frequency == 0:
                period = 0
            else:
                period = 1 / frequency
            wave_ids[index] = self.utils.create_wave(period)

        # generate number of steps per frequency
        chain = []
        for index, step in enumerate(steps):
            steps_number_below_256 = step & 255
            steps_number_times_256 = step >> 8

            chain += [
                255,
                0,
                wave_ids[index],
                255,
                1,
                steps_number_below_256,
                steps_number_times_256,
            ]

        self.pi.wave_chain(chain)  # Transmit chain.

        while self.pi.wave_tx_busy():  # While transmitting.
            await asyncio.sleep(0.01)

        # delete all waves
        for index in range(len(wave_ids)):
            self.pi.wave_delete(index)

    async def run_moves(self, data):
        self.pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
        self.pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)

        self.hardware.end = False  # may cause bugs

        # ticker = tick_response(data)
        positions_len = len(data)
        current_index = 0
        start_time = time.time()

        while not self.pi.wave_tx_busy():
            desired_position = data[current_index] * self.settings.max_steps
            forward = desired_position > self.hardware.position
            self.pi.write(config.DIRECTION_PIN, forward)
            steps = int(abs(desired_position - self.hardware.position))
            # print('s', steps)

            force = device.read_num()[0]
            # measure force only against the current direction
            force = -force if forward else force  # initial force value is inverted
            if force < 0:
                force = 0

            # print('f', force)

            if steps > 0:
                # old_steps = steps
                force_fraction = force / self.settings.force_limit
                steps_limit_percentage = self.settings.stroke_force_chart[
                    int(min(force_fraction * 1000, 999))
                ]
                steps_limit = int(
                    steps_limit_percentage
                    / 100
                    * self.settings.tick_stroke_limit
                    * self.settings.steps_per_mm
                )
                steps = min(steps, steps_limit)
                # print('steps', old_steps, steps, 'force', force, 'limit', steps_limit)

                if steps == 0:
                    steps = 1  # todo: wait instead of moving
                if forward:
                    self.hardware.position += steps
                else:
                    self.hardware.position -= steps

                self.pi.wave_clear()
                wave_id = self.utils.create_wave_pad(
                    1 / (steps * self.settings.wave_resolution)
                )

                # generate number of steps per frequency
                steps_number_below_256 = steps & 255
                steps_number_times_256 = steps >> 8

                chain = [
                    255,
                    0,
                    wave_id,
                    255,
                    1,
                    steps_number_below_256,
                    steps_number_times_256,
                ]

                self.pi.wave_chain(chain)  # Transmit chain.

                while self.pi.wave_tx_busy():  # While transmitting.
                    await asyncio.sleep(0.01)

                # delete all waves
                self.pi.wave_delete(0)

            current_index += 1
            if current_index == positions_len:
                if self.hardware.end:
                    break
                else:
                    current_index = 0
                    print("Wave time: " + str(time.time() - start_time))
                    start_time = time.time()


def tick_response(data):
    batch_counter = 0
    batch = []
    reverse = data[0] < 0
    for point in data:
        if point < 0:
            point_reverse = True
        else:
            point_reverse = False

        if point_reverse != reverse:
            yield reverse, batch
            batch = [point]
            batch_counter = 0
            reverse = point_reverse
        else:
            batch.append(point)
            batch_counter += 1
            if (
                batch_counter == 19
            ):  # pigpio doesn't accept more than 20 waves per chain
                yield point_reverse, batch
                batch = []
                batch_counter = 0
                reverse = point_reverse
    yield reverse, batch
