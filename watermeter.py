#!/usr/bin/python
import sys

import RPi.GPIO as GPIO
import time
import os
import paho.mqtt.client as mqtt
import logging

# Watermeter stand (will only be used when there is nog meterstand_water.txt file)
# global counter
counter = 0

# MQTT URL
mqtt_host = os.getenv('MQTT_HOST')
mqtt_port = os.getenv('MQTT_PORT')
mqtt_topic = os.getenv('MQTT_TOPIC')

# filename for persisting data local
fileName = "/usr/src/app/config/meterstand_water.txt"

# Pin property (pin 9 is GPIO 21)
gpio_pin = 9

# logging.basicConfig(filename='watermeter.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('watermeter')

logger.info('Script started')

# Open meterstand.txt file and read meterstand
# If meterstand.txt does not exist it will create the file and add the meterstand of Counter to it
fn = fileName
if os.path.exists(fn):
    f = open(fn, "r+")
    inhoud = f.readline()
    a, b, c = inhoud.split()
    counter = int(c)
else:
    f = open(fn, "w")
    f.write('meterstand = ' + repr(counter))
    f.close()

# Board is pin nr, BMC is GPIO nr
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# Functie  callback
# This function will be called when an interrupt happens
def Interrupt(channel):
    logger.info('Callback function called!')
    time.sleep(0.05)  # need to filter out the false positive of some power fluctuation
    if GPIO.input(gpio_pin) == 0:
        logger.warning('quitting event handler because this was probably a false positive')
        return
    # counter will count every interrupt and add Couter with 0.5l (deler watermeter will be set on 10)
    f = open(fn, "r+")
    inbound = f.readline()
    a, b, c = inbound.split()
    counter = int(c)
    counter = counter + 1
    f.close()
    # Write counter to file
    f = open(fn, 'w')
    f.write('meterstand = ' + repr(counter))
    f.close()
    # Send JSON TO MQTT
    try:
        client = mqtt.Client()
        client.connect(mqtt_host, int(mqtt_port), 60)
        client.publish(mqtt_topic, payload=counter, qos=0, retain=False)
        client.disconnect()
        logger.info("Watermeter counter = " + str(counter))
    except:
        logger.error("Could not sent message to MQTT server!")


# Interrupt-Event toevoegen, sensor geeft een 0 en en bij detectie een 1
# Bij detectie een 1 daarom check stijgende interrupt.
GPIO.add_event_detect(gpio_pin, GPIO.RISING, callback=Interrupt, bouncetime=200)

try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()
    logger.warning("\nBye")
