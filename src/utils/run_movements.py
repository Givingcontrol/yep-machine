import asyncio

import pigpio

import config
from utils.wave import create_wave


async def generate_ramp(pi, steps):
    pi.wave_clear()
    wave_ids = [-1] * len(steps)

    # generate wave period
    for index, step in enumerate(steps):
        # todo: fix timing, not quite per second, more like per 1.5 seconds
        frequency = step * config.WAVE_RESOLUTION * 2
        if frequency == 0:
            period = 0
        else:
            period = 1 / frequency
        wave_ids[index] = create_wave(pi, period)

    # generate number of steps per frequency
    chain = []
    for index, step in enumerate(steps):
        steps_number_below_256 = step & 255
        steps_number_times_256 = step >> 8

        chain += [255, 0, wave_ids[index], 255, 1, steps_number_below_256, steps_number_times_256]

    pi.wave_chain(chain)  # Transmit chain.

    while pi.wave_tx_busy():  # While transmitting.
        await asyncio.sleep(0.01)

    # delete all waves
    for index in range(len(wave_ids)):
        pi.wave_delete(index)


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
            if batch_counter == 19:  # pigpio doesn't accept more than 20 waves per chain
                yield point_reverse, batch
                batch = []
                batch_counter = 0
                reverse = point_reverse
    yield reverse, batch


async def run_movements(pi, data):
    pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
    pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)
    ticker = tick_response(data)

    for reverse, moves in ticker:
        pi.write(config.DIRECTION_PIN, reverse)
        # todo: raise exception instead of silently correcting movement value with max
        steps = [int(min(abs(move), 1) * config.MAX_STEPS) for move in moves]
        await generate_ramp(pi, steps)

        pi.wave_tx_stop()  # stop waveform
        pi.wave_clear()
