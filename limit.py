import RPi.GPIO as GPIO
import time

LOW_PIN  = 22
HIGH_PIN = 23

if __name__ == "__main__":
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
    GPIO.setup(LOW_PIN, GPIO.IN)
    GPIO.setup(HIGH_PIN, GPIO.IN)

    while(True):
        print(GPIO.input(LOW_PIN))
        print(GPIO.input(HIGH_PIN))
        time.sleep(2)