import pigpio

import config


def create_wave(pi, period):
    period = int(period * 1000000)  # convert s to ns
    wave = [
        pigpio.pulse(1 << config.PULSE_PIN, 0, period),
        pigpio.pulse(0, 1 << config.PULSE_PIN, period),
    ]
    pi.wave_add_generic(wave)
    return pi.wave_create()
