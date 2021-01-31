class UpdateSettings:
    def __init__(self, context):
        self.hardware = context.hardware
        self.settings = context.settings

    async def run(self):
        self.hardware.end = True
        self.settings.update_settings()
