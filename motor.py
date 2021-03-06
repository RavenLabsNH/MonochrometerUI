from DRV8825 import DRV8825


class Motor:
    def __init__(self, running_flag, current_position, steps_per_nm):
        self.motor1 = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27),
                              running_flag=running_flag, current_position=current_position, steps_per_nm=steps_per_nm)

        self.motor1.SetMicroStep('softward', 'fullstep')

    def move_monochrom_backward_steps(self, number_of_steps, disable=True):
        steps = int(number_of_steps)
        self.motor1.TurnStep(
            Dir='backward', steps=steps)
        if disable:
            self.motor1.Stop()

    def move_monochrom_forward_steps(self, number_of_steps, disable=True):
        steps = int(number_of_steps)
        self.motor1.TurnStep(
            Dir='forward', steps=steps)
        if disable:
            self.motor1.Stop()

    def move_monochrom_forward_continuous(self, disable=True):
        print("move_monochrom_forward_continuous")
        self.motor1.TurnContinous(dir='forward')
        if disable:
            self.motor1.Stop()

    def move_monochrom_backward_continuous(self, disable=True):
        print("move_monochrom_backward_continuous")
        self.motor1.TurnContinous(dir='backward')
        if disable:
            self.motor1.Stop()

    def stop_motor(self):
        self.motor1.Stop()
