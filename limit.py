import RPi.GPIO as GPIO
import time

LOW_PIN = 24
HIGH_PIN = 23

if __name__ == "__main__":
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
    GPIO.setup(LOW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(HIGH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while(True):
        print("Low" + str(GPIO.input(LOW_PIN)))
        print("High" + str(GPIO.input(HIGH_PIN)))
        time.sleep(2)