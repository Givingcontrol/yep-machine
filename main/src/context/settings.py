import requests

import config

ALLOWED_KEYS = (
    "wave_resolution",
    "stroke_limit",
    "max_steps",
    "stroke_length",
    "microsteps_per_rev",
    "padding_steps",
)


class Settings:
    def __init__(self):
        self.wave_resolution = None
        self.stroke_limit = None
        self.max_steps = None
        self.stroke_length = None
        self.microsteps_per_rev = None
        self.padding_steps = None

    def set_settings(self, data):
        for key in ALLOWED_KEYS:
            if key in data:
                setattr(self, key, data[key])

    def update_settings(self):
        data = requests.get(f"{config.API_URL}settings/machine-thrust/default/").json()
        self.set_settings(data)
