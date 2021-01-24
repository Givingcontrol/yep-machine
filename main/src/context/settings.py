import json

import requests

import config

ALLOWED_KEYS = (
    "wave_resolution",
    "stroke_limit",
    "max_steps",
    "max_stroke",
    "microsteps_per_rev",
    "padding_mm",
)


class Settings:
    def __init__(self):
        self.wave_resolution = None
        self.stroke_limit = None
        self.max_steps = None
        self.max_stroke = None
        self.microsteps_per_rev = None

        self.padding_steps = None

    def update_settings(self, data=None):
        if data:
            response = requests.put(
                f"{config.API_URL}settings/machine-thrust/default/", json.dumps(data)
            )
            data = response.json()
        else:
            data = requests.get(
                f"{config.API_URL}settings/machine-thrust/default/"
            ).json()

        for key in ALLOWED_KEYS:
            if key in data:
                setattr(self, key, data[key])
