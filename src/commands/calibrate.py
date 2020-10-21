import asyncio

import pigpio
from gpiozero import Button

import config
from utils.wave import create_wave

front_limit = Button(21, pull_up=True)
back_limit = Button(20, pull_up=True)

pi = pigpio.pi()


async def calibrate(pi, ws):
    # todo: increase calibration speed, first multiple steps per check, then finer adjustments

    pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
    pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)
    pi.wave_clear()

    wave = create_wave(pi, 10000)

    # go to the back
    pi.write(config.DIRECTION_PIN, False)
    while not back_limit.is_pressed:
        if front_limit.is_pressed:
            raise Exception("Wrong direction")

        await asyncio.sleep(0)
        if not pi.wave_tx_busy():
            # todo: check why WAVE_MODE_ONE_SHOT_SYNC queues too many waves that keep running
            pi.wave_send_using_mode(wave, pigpio.WAVE_MODE_ONE_SHOT)

    # go to the front while counting steps
    pi.write(config.DIRECTION_PIN, True)
    steps_counter = 0
    while not front_limit.is_pressed:
        if steps_counter > 10 and back_limit.is_pressed:
            raise Exception("Wrong direction")

        await asyncio.sleep(0)
        if not pi.wave_tx_busy():
            steps_counter += 1
            pi.wave_send_using_mode(wave, pigpio.WAVE_MODE_ONE_SHOT)

    print(steps_counter)

    pi.wave_tx_stop()
    pi.wave_clear()
