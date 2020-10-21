from gpiozero import Button

front_limit = Button(21)
back_limit = Button(20)


def calibrate(status_ws):
    print("calibrate")
    # run_movements()
    while back_limit.is_pressed:
        pass
