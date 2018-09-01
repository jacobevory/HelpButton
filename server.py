
import RPi.GPIO as GPIO
import time
import pika
import sys
import os
import json
import threading

GPIO.setmode(GPIO.BOARD)

AMBER_LIGHT = 11
RED_LIGHT = 13
HORN = 15
ON = GPIO.HIGH
OFF = GPIO.LOW

GPIO.setwarnings(False)
GPIO.setup([AMBER_LIGHT, RED_LIGHT, HORN], GPIO.OUT, initial=GPIO.LOW)


credentials = pika.PlainCredentials('lobby', 'button')
parameters = pika.ConnectionParameters(host='localhost', credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue='signal', arguments={'x-message-ttl' : 1000})


button_active = 0
switch_active = 1

def controller_thread():
	
	def callback(ch, method, properties, body):
		global button_active
		global switch_active
		data_in = body.decode()
		print (data_in)
		print(" [x] Received %r" % data_in)
		j = json.loads(data_in)
		if int(j["Button"]) == 1:
			print("Success")
			button_active = 1
			switch_active = 0
		elif int(j['Switch']) == 0:
			button_active = 0
			switch_active = 0
		elif int(j['Switch']) == 1:
			button_active = 0
			switch_active = 1
		
	while True:
		try:
			print("HELLO")
			channel.basic_consume(callback,
							  queue='signal',
							  no_ack=True)
			channel.start_consuming()
		except KeyboardInterrupt:
			return
		except:
			pass

if __name__ == '__main__':
	global button_active
	global switch_active
	try:
		t = threading.Thread(target=controller_thread)
		t.start()
		print("thread started")
		count = 0
		while True:
			print(str(button_active) + " , " + str(switch_active))
			if button_active == 1:
				GPIO.output(AMBER_LIGHT, OFF)
				if count % 2 == 0:
					GPIO.output(RED_LIGHT, ON)
				else:
					GPIO.output(RED_LIGHT, OFF)
				if count % 5 == 0:
					GPIO.output(HORN, ON)
				else:
					GPIO.output(HORN, OFF)
				count = count + 1
			elif switch_active == 0:
				GPIO.output(RED_LIGHT, OFF)
				GPIO.output(HORN, OFF)
				GPIO.output(AMBER_LIGHT, OFF)
				count = 0
			elif switch_active == 1:
				GPIO.output(RED_LIGHT, OFF)
				GPIO.output(HORN, OFF)
				GPIO.output(AMBER_LIGHT, ON)
				count = 0
				
			time.sleep(0.5)
					
    # Stop on Ctrl+C and clean up
	except KeyboardInterrupt:
		pass
	finally:
		GPIO.output(AMBER_LIGHT, GPIO.LOW)
		GPIO.output(RED_LIGHT, GPIO.LOW)
		GPIO.output(HORN, GPIO.LOW)
		#os.execv(sys.executable, ['python3'] + sys.argv)
        