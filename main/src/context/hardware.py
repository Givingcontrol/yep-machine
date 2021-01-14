import pigpio
from gpiozero import Button

import config


class Hardware:
    def __init__(self):
        self.pi = pigpio.pi()

        self.pi.set_mode(config.PULSE_PIN, pigpio.OUTPUT)
        self.pi.set_mode(config.DIRECTION_PIN, pigpio.OUTPUT)
        self.pi.wave_tx_stop()
        self.pi.wave_clear()

        self.front_limit = Button(21)
        self.back_limit = Button(20)

        self.position = None

        self.enable_limit_monitoring()

    @property
    def limit_pressed(self):
        return self.front_limit.is_pressed or self.back_limit.is_pressed

    def reset(self, message):
        print("RESET", message)
        self.pi.set_mode(config.PULSE_PIN, pigpio.INPUT)
        self.pi.wave_tx_stop()
        self.pi.wave_clear()

    def enable_limit_monitoring(self):
        self.front_limit.when_pressed = lambda: self.reset("Front limit switch pressed")
        self.back_limit.when_pressed = lambda: self.reset("Back limit switch pressed")

    def disable_limit_monitoring(self):
        self.front_limit.when_pressed = None
        self.back_limit.when_pressed = None

    def check(self):
        pass
        # if not front_limit.is_press

    def setup_limit_buttons(self):
        pass
