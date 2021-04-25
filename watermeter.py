#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os
import paho.mqtt.client as mqtt

#Watermeter stand (will only be used when there is nog meterstand_water.txt file)
global Counter
Counter = 0

#MQTT URL
mqtt_host = "localhost"
mqtt_port = 1883
mqtt_topic = "watermeter"

#filename for persisting data local
fileName = "/home/user/meterstand_water.txt"

#Pin property (pin 40 is GPIO 21)
gpio_pin = 40

#Open meterstand.txt file and read meterstand
#If meterstand.txt does not exist it will create the file and add the meterstand of Counter to it
fn = fileName
if os.path.exists(fn):
    f = open(fn, "r+")
    inhoud = f.readline()
    a,b,c = inhoud.split()
    Counter = int(c)
else:
    f = open(fn, "w")
    f.write( 'meterstand = ' + repr(Counter))
    f.close()

#Board is pin nr, BMC is GPIO nr
GPIO.setmode(GPIO.BOARD)
GPIO.setup(gpio_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#Functie  callback
#This function will be called when an interrupt happens
def Interrupt(channel):
    print('Callback function called!')
    time.sleep(0.05)         # need to filter out the false positive of some power fluctuation
    if GPIO.input(40) == 0:
       print('quitting event handler because this was probably a false positive')
       return
    #Counter will count every interrupt and add Couter with 0.5l (deler watermeter will be set on 10)
    f = open(fn, "r+")
    inhoud = f.readline()
    a,b,c = inhoud.split()
    Counter = int(c)
    Counter = Counter + 1
    f.close()
    #Write counter to file
    f = open( fn, 'w')
    f.write( 'meterstand = ' + repr(Counter))
    f.close()
    #Send JSON TO MQTT
    client = mqtt.Client()
    client.connect(mqtt_host, mqtt_port, 60)
    client.publish(mqtt_topic, payload=Counter, qos=0, retain=False)
    client.disconnect()
    print("Watermeter Counter = " + str(Counter))

#Interrupt-Event toevoegen, sensor geeft een 0 en en bij detectie een 1
#Bij detectie een 1 daarom check stijgende interrupt.
GPIO.add_event_detect(40, GPIO.RISING, callback = Interrupt, bouncetime = 200)

try:
    while True:
      time.sleep(0.2)        
except KeyboardInterrupt:
  GPIO.cleanup()
  print("\nBye")
