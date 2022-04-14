from DRV8825 import DRV8825


class Motor:
    def __init__(self):
        self.motor1 = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

        self.motor1.SetMicroStep('softward', 'fullstep')

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
