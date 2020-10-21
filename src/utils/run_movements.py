import asyncio

import pigpio

import config
from utils.wave import create_wave


async def generate_ramp(pi, ramp):
    pi.wave_clear()
    ramp_len = len(ramp)
    wave_id = [-1] * ramp_len

    # generate a wave per frequency
    for i in range(ramp_len):
        f = ramp[i][0]
        if f == 0:
            micros = 0
        else:
            micros = int(500000 / f)

        wave_id[i] = create_wave(pi, micros)

    # generate a chain of waves
    chain = []
    for i in range(ramp_len):
        steps = ramp[i][1]
        x = steps & 255
        y = steps >> 8

        chain += [255, 0, wave_id[i], 255, 1, x, y]

    pi.wave_chain(chain)  # Transmit chain.

    while pi.wave_tx_busy():  # While transmitting.
        await asyncio.sleep(0.01)

    # delete all waves
    for i in range(ramp_len):
        pi.wave_delete(wave_id[i])


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
            if batch_counter == 19:
                yield point_reverse, batch
                batch = []
                batch_counter = 0
                reverse = point_reverse
    yield reverse, batch


async def run_movements(pi, data):
    pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
    pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)
    ticker = tick_response(data)
    for reverse, tick in ticker:
        pi.write(config.DIRECTION_PIN, reverse)
        group = []
        for point in tick:
            frequency = abs(int(point * config.MAX_FREQUENCY))
            group.append([frequency, int(frequency / config.POINTS_IN_WAVE)])
        await generate_ramp(pi, group)

        pi.wave_tx_stop()  # stop waveform
        pi.wave_clear()
