import platform
if platform.machine() == 'AMD64':
    PI = False
else:
    PI = True

if PI:
    import RPi.GPIO as GPIO
import time

LOW_PIN = 25
HIGH_PIN = 23

MotorDir = [
    'backward',
    'forward',
]

ControlMode = [
    'hardward',
    'softward',
]

class DRV8825():
    def __init__(self, dir_pin, step_pin, enable_pin, mode_pins, running_flag, current_position, steps_per_nm):
        self.dir_pin = dir_pin
        self.step_pin = step_pin        
        self.enable_pin = enable_pin
        self.mode_pins = mode_pins
        self.running_flag = running_flag
        self.current_position = current_position
        self.steps_per_nm = steps_per_nm

        if PI:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(LOW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(HIGH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.dir_pin, GPIO.OUT)
            GPIO.setup(self.step_pin, GPIO.OUT)
            GPIO.setup(self.enable_pin, GPIO.OUT)
            GPIO.setup(self.mode_pins, GPIO.OUT)
        
    def digital_write(self, pin, value):
        if PI:
            GPIO.output(pin, value)
        pass

    def Stop(self):
        self.digital_write(self.enable_pin, 0)
    
    def SetMicroStep(self, mode, stepformat):
        """
        (1) mode
            'hardward' :    Use the switch on the module to control the microstep
            'software' :    Use software to control microstep pin levels
                Need to put the All switch to 0
        (2) stepformat
            ('fullstep', 'halfstep', '1/4step', '1/8step', '1/16step', '1/32step')
        """
        microstep = {'fullstep': (0, 0, 0),
                     'halfstep': (1, 0, 0),
                     '1/4step': (0, 1, 0),
                     '1/8step': (1, 1, 0),
                     '1/16step': (0, 0, 1),
                     '1/32step': (1, 0, 1)}

        print("Control mode:" + mode)
        if (mode == ControlMode[1]):
            print("set pins")
            self.digital_write(self.mode_pins, microstep[stepformat])
        
    def TurnStep(self, Dir, steps, stepdelay=0.0000005):
        if not PI:
            stepdelay = 0.000000005
        if (Dir == MotorDir[0]):
            print("backward")
            self.digital_write(self.enable_pin, 1)
            self.digital_write(self.dir_pin, 0)
        elif (Dir == MotorDir[1]):
            print("forward")
            self.digital_write(self.enable_pin, 1)
            self.digital_write(self.dir_pin, 1)
        else:
            print("the dir must be : 'forward' or 'backward'")
            self.digital_write(self.enable_pin, 0)
            return

        if (steps == 0):
            return
            
        print("turn step: " + str(steps))
        for i in range(steps):
            if self.running_flag.value is not True:
                break
            if PI:
                if (Dir == MotorDir[0]) and GPIO.input(LOW_PIN) == 0:
                    self.running_flag.value = False
                    print("Low triggerd: " + MotorDir[0] + " " + str(GPIO.input(LOW_PIN)))
                    break
                if (Dir == MotorDir[1]) and GPIO.input(HIGH_PIN) == 0:
                    self.running_flag.value = False
                    print("High triggerd " + MotorDir[1] + " " + str(GPIO.input(HIGH_PIN)))
                    break
            self.digital_write(self.step_pin, True)
            time.sleep(stepdelay)
            self.digital_write(self.step_pin, False)
            if (Dir == MotorDir[0]):
                self.current_position.value = self.current_position.value - (1 / self.steps_per_nm)
            else:
                self.current_position.value = self.current_position.value + (1 / self.steps_per_nm)


    def TurnContinous(self, dir, stepdelay=0.0000005):
        if (dir == MotorDir[0]):
            print("backward")
            self.digital_write(self.enable_pin, 1)
            self.digital_write(self.dir_pin, 0)
        elif (dir == MotorDir[1]):
            print("forward")
            self.digital_write(self.enable_pin, 1)
            self.digital_write(self.dir_pin, 1)
        else:
            print("the dir must be : 'forward' or 'backward'")
            self.digital_write(self.enable_pin, 0)

        while self.running_flag.value == True:
            if PI:
                if (dir == MotorDir[0]) and GPIO.input(LOW_PIN) == 0:
                    self.running_flag.value = False
                    print("Low triggerd: " + MotorDir[0] + " " + str(GPIO.input(LOW_PIN)))
                    break
                if (dir == MotorDir[1]) and GPIO.input(HIGH_PIN) == 0:
                    self.running_flag.value = False
                    print("High triggerd " + MotorDir[1] + " " + str(GPIO.input(HIGH_PIN)))
                    break
            self.digital_write(self.step_pin, True)
            time.sleep(stepdelay)
            self.digital_write(self.step_pin, False)
            if (dir == MotorDir[0]):
                self.current_position.value = self.current_position.value - (1/self.steps_per_nm)
            else:
                self.current_position.value = self.current_position.value + (1 / self.steps_per_nm)