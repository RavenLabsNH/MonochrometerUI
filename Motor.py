from DRV8825 import DRV8825


class Motor:
    def __init__(self):
        self.motor1 = DRV8825(dir_pin=13, step_pin=19,
                              enable_pin=12, mode_pins=(16, 17, 20))
        self.motor1.SetMicroStep('softward', '1/32step')

    def move_monochrom_backward(self, number_of_steps, disable=True):
        steps = int(number_of_steps)
        self.motor1.TurnStep(
            Dir='forward', steps=steps)
        if disable:
            self.motor1.Stop()

    def move_monochrom_forward(self, number_of_steps, disable=True):
        steps = int(number_of_steps)
        self.motor1.TurnStep(
            Dir='backward', steps=steps)
        if disable:
            self.motor1.Stop()

    def stop_motor(self):
        self.motor1.Stop()
