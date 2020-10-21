import pigpio

import config


def create_wave(pi, frequency):
    wave = [
        pigpio.pulse(1 << config.PULSE_PIN, 0, frequency),
        pigpio.pulse(0, 1 << config.PULSE_PIN, frequency),
    ]
    pi.wave_add_generic(wave)
    return pi.wave_create()
