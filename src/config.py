# max allowed by pigpio without encountering "pigpio.error: 'too many chain counters'"
WAVE_RESOLUTION = 20.0  # number of frequency changes per second
MAX_STEPS = 1838 / 2.5
PADDING_STEPS = 80

SERVER_URL = "10.0.0.2"

WS_URL = f"ws://{SERVER_URL}/api/stream/"

PULSE_PIN = 17
DIRECTION_PIN = 27
