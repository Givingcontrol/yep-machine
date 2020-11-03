from context.hardware import Hardware
from context.settings import Settings
from context.utils import Utils


class Context:
    def __init__(self):
        self.hardware = Hardware()
        self.pi = self.hardware.pi
        self.settings = Settings()
        self.utils = Utils(self.hardware, self.settings)

        self.settings.update_settings()
