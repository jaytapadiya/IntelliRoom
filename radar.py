from gpiozero import DigitalInputDevice
from time import sleep
import datetime

radar = DigitalInputDevice(17, pull_up=False, bounce_time=2.0)

def detector():
    timestamp = str((datetime.datetime.now()))
    timestamp = timestamp[0:19]
    print("Motion captured: ", timestamp)

while True:
    radar.when_activated = detector
    sleep(5)
