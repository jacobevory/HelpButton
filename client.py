
import RPi.GPIO as GPIO
import os
import time
import sys
import pika
from client_config import serverIP, user, password, queueName

GPIO.setmode(GPIO.BOARD)

BUTTON_LIGHT = 11
BUTTON_INPUT = 13
SWITCH_INPUT = 15

ON = GPIO.HIGH
OFF = GPIO.LOW

GPIO.setwarnings(False)
GPIO.setup(BUTTON_LIGHT, GPIO.OUT, initial=OFF)

GPIO.setup([BUTTON_INPUT, SWITCH_INPUT], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

count = 0
button_active = 0
switch_active = 1
send_active = 0

credentials = pika.PlainCredentials(user, password)
parameters = pika.ConnectionParameters(host=serverIP, credentials=credentials)
connection = pika.BlockingConnection(parameters)


def sendData():
	global button_active
	global switch_active
	global send_active
	
	sendBody = "{\"Button\":\"" + str(button_active) + "\", \"Switch\":\"" + str(switch_active) + "\"}"
#	channel = connection.channel()
#	channel.queue_declare(queue=queueName, arguments={'x-message-ttl' : 10000})

	channel.basic_publish(exchange='',
				  routing_key=queueName,
				  body=sendBody)
	print(sendBody)
	send_active = 0
	
def buttonPressed(self):
	global button_active
	global switch_active
	global send_active
	global count
	if switch_active == 1:
		button_active = 1
	count = 0
#		sendData()

def switchFlipped(self):
	global button_active
	global switch_active
	global send_active
	global count
	button_active = 0
	time.sleep(0.1)
	if GPIO.input(SWITCH_INPUT):
		switch_active = 1
	else:
		switch_active = 0
	count = 0
#	sendData()
	
	
GPIO.add_event_detect(BUTTON_INPUT, GPIO.RISING, buttonPressed)
GPIO.add_event_detect(SWITCH_INPUT, GPIO.BOTH, switchFlipped)

if __name__ == '__main__':
	global count
	try:
		switch_active = GPIO.input(SWITCH_INPUT)
		channel = connection.channel()
		channel.queue_declare(queue=queueName, arguments={'x-message-ttl' : 2000})

		count = 0
		while True:
			if switch_active and not button_active:
				GPIO.output(BUTTON_LIGHT, ON)
			elif switch_active and button_active:
				if count % 10 == 0:
					GPIO.output(BUTTON_LIGHT, ON)
				else:
					GPIO.output(BUTTON_LIGHT, OFF)
			else:
				GPIO.output(BUTTON_LIGHT, OFF)	
			if count % 5 == 0:
				sendData()
			if count > 600:
				switch_active = 1;
			count = count + 1
			if count >= 65535:
				count = 0
#			print(str(button_active) + " , " + str(switch_active))
#			if send_active == 1:
#				sendData()
			time.sleep(0.1)
	except KeyboardInterrupt:   # Ctrl+C
		 connection.close()
	finally:
		 GPIO.output(BUTTON_LIGHT, GPIO.LOW)
		 os.execv(sys.executable, ['python3'] + sys.argv)
