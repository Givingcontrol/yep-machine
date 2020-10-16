from gpiozero import Button

from common.run_movements import run_movements

front_limit = Button(21)
back_limit = Button(20)


def calibrate(status_ws):
    print('calibrate')
    # run_movements()