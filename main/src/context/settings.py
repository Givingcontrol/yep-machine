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
    "steps_per_mm",
    "tick_stroke_limit",
    "force_limit"
)


class Settings:
    def __init__(self):
        self.wave_resolution = None
        self.stroke_limit = None
        self.max_steps = None
        self.max_stroke = None
        self.microsteps_per_rev = None
        self.steps_per_mm = None
        self.tick_stroke_limit = None
        self.force_limit = None

        self.padding_steps = None
        self.stroke_force_chart = None

        self.update_settings()

    def update_settings(self, data=None):
        if data:
            response = requests.put(
                f"{config.API_URL}settings/machine-thrust/default/?machine=true",
                json.dumps(data),
            )
            data = response.json()
        else:
            data = requests.get(
                f"{config.API_URL}settings/machine-thrust/default/"
            ).json()

        for key in ALLOWED_KEYS:
            if key in data:
                setattr(self, key, data[key])

        self.stroke_force_chart = requests.post(
            f"{config.API_URL}curve/", json.dumps({"points": data["stroke_force_chart"], "resolution": 1000})
        ).json()
