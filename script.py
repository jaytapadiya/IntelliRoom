'''
**********************************************************************
* Filename    : dht11.py
* Description : test for SunFoudner DHT11 humiture & temperature module
* Author      : Dream
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Dream    2016-09-30    New release
**********************************************************************
'''
#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from datetime import datetime
from sns_formatter import SnsFormatter
import os
import json

DHTPIN = 6 #HUMITURE SENSOR
MOTION_SENSOR_1_PIN = 25
MOTION_SENSOR_2_PIN = 17
FLAME_SENSOR_PIN = 2
GAS_SENSOR_PIN = 3
SOUND_SENSOR_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTION_SENSOR_1_PIN,GPIO.IN)
GPIO.setup(MOTION_SENSOR_2_PIN,GPIO.IN) 
GPIO.setup(SOUND_SENSOR_PIN,GPIO.IN)

MAX_UNCHANGE_COUNT = 100

STATE_INIT_PULL_DOWN = 1
STATE_INIT_PULL_UP = 2
STATE_DATA_FIRST_PULL_DOWN = 3
STATE_DATA_PULL_UP = 4
STATE_DATA_PULL_DOWN = 5

last_sns_message_time = datetime.now()


def read_dht11_dat():
	GPIO.setup(DHTPIN, GPIO.OUT)
	GPIO.output(DHTPIN, GPIO.HIGH)
	time.sleep(0.05)
	GPIO.output(DHTPIN, GPIO.LOW)
	time.sleep(0.02)
	GPIO.setup(DHTPIN, GPIO.IN, GPIO.PUD_UP)

	unchanged_count = 0
	last = -1
	data = []
	while True:
		current = GPIO.input(DHTPIN)
		data.append(current)
		if last != current:
			unchanged_count = 0
			last = current
		else:
			unchanged_count += 1
			if unchanged_count > MAX_UNCHANGE_COUNT:
				break

	state = STATE_INIT_PULL_DOWN

	lengths = []
	current_length = 0

	for current in data:
		current_length += 1

		if state == STATE_INIT_PULL_DOWN:
			if current == GPIO.LOW:
				state = STATE_INIT_PULL_UP
			else:
				continue
		if state == STATE_INIT_PULL_UP:
			if current == GPIO.HIGH:
				state = STATE_DATA_FIRST_PULL_DOWN
			else:
				continue
		if state == STATE_DATA_FIRST_PULL_DOWN:
			if current == GPIO.LOW:
				state = STATE_DATA_PULL_UP
			else:
				continue
		if state == STATE_DATA_PULL_UP:
			if current == GPIO.HIGH:
				current_length = 0
				state = STATE_DATA_PULL_DOWN
			else:
				continue
		if state == STATE_DATA_PULL_DOWN:
			if current == GPIO.LOW:
				lengths.append(current_length)
				state = STATE_DATA_PULL_UP
			else:
				continue
	if len(lengths) != 40:
		#print ("Data not good, skip")
		return False

	shortest_pull_up = min(lengths)
	longest_pull_up = max(lengths)
	halfway = (longest_pull_up + shortest_pull_up) / 2
	bits = []
	the_bytes = []
	byte = 0

	for length in lengths:
		bit = 0
		if length > halfway:
			bit = 1
		bits.append(bit)
	#print ("bits: %s, length: %d" % (bits, len(bits)))
	for i in range(0, len(bits)):
		byte = byte << 1
		if (bits[i]):
			byte = byte | 1
		else:
			byte = byte | 0
		if ((i + 1) % 8 == 0):
			the_bytes.append(byte)
			byte = 0
	#print (the_bytes)
	checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
	if the_bytes[4] != checksum:
		#print ("Data not good, skip")
		return False

	return the_bytes[0], the_bytes[2]

def publish_to_sns(snsItem):
    if type(snsItem) is not SnsFormatter:
        raise Exception("Wrong snsItem format")
    global last_sns_message_time
    difference = datetime.now() - last_sns_message_time
    if difference.total_seconds() >= 5:
        #SNS_BASH_CMD = "aws sns publish --topic-arn arn:aws:sns:us-east-1:728853861485:IntelliRoomStatusNotification --message \"%s\""
        message = messageFormatter(snsItem)
		print(message)
        #os.system(SNS_BASH_CMD % message)
        last_sns_message_time = datetime.now()

def messageFormatter(snsItem):
	outString = "{}: {} sensor".format(snsItem.eventType,snsItem.sensorType.lower())
	switch = {
		snsItem.Sensors.TEMPERATURE: " at {} degrees".format(snsItem.sensorValue),
		snsItem.Sensors.HUMIDITY: " at {}\% humidity".format(snsItem.sensorValue),
		snsItem.Sensors.MOTION: " activated",
		snsItem.Sensors.SOUND: " activated"
	}
	outString += switch.get(snsItem.sensorType, "Invalid sensor")
	return outString

def check_humiture():
	result = read_dht11_dat()
	if result:
		humidity, temperature = result
		print ("humidity: %s %%,  Temperature: %s C`" % (humidity, temperature))
		if int(humidity) >= 70: #70% humidity
			return SnsFormatter(
				SnsFormatter.Events.WARNING,
				SnsFormatter.Sensors.HUMIDITY,
				int(humidity))
		if int(temperature) >= 26: #26 degrees Celsius
			return SnsFormatter(
				SnsFormatter.Events.WARNING,
				SnsFormatter.Sensors.TEMPERATURE,
				int(temperature))
	return None

def check_motion_sensor():
	if(GPIO.input(MOTION_SENSOR_1_PIN)==True) and (GPIO.input(MOTION_SENSOR_2_PIN)==True): #object is far away
		return SnsFormatter(
			SnsFormatter.Events.INFO,
			SnsFormatter.Sensors.MOTION,
			None)
	return None

def callback(channel):
	if not GPIO.input(channel):
		publish_to_sns(SnsFormatter(SnsFormatter.Events.WARNING, SnsFormatter.Sensors.SOUND, None))

GPIO.add_event_detect(SOUND_SENSOR_PIN, GPIO.BOTH, bouncetime=30)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(SOUND_SENSOR_PIN, callback)  # assign function to GPIO PIN, Run function on change

def main():
    while True:
        humiture = check_humiture()
		if humiture: 
			publish_to_sns(humiture)
		motion = check_motion_sensor()
		if motion:
			publish_to_sns(motion)
        time.sleep(0.5)

def destroy():
	GPIO.cleanup()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		destroy() 
