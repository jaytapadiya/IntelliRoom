import RPi.GPIO as IO
import time
IO.setwarnings(False)
IO.setmode(IO.BCM)

IO.setup(4,IO.IN) #GPIO 14 -> IR sensor as input

while 1:

    time.sleep(2)

    if(IO.input(4)==True): #object is far away
        continue 
    if(IO.input(4)==False): #object is near
        print("Object near")
