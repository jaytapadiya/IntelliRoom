import RPi.GPIO as IO
import time
import datetime
IO.setwarnings(False)
IO.setmode(IO.BCM)

IO.setup(4,IO.IN) #GPIO 14 -> IR sensor as input
IO.setup(17,IO.IN) 
    
current_time = datetime.datetime.now()


while 1:

    time.sleep(2)
    if(IO.input(4)==True) and (IO.input(17)==True): #object is far away
        continue 
    if(IO.input(4)==False) and (IO.input(17)==False): #object is neari
        global current_time
        difference = datetime.datetime.now() - current_time
        if difference.total_seconds() >= 5:
            current_time = datetime.datetime.now()
            print(current_time)
