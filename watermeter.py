#!/usr/bin/python
import sys
import time
import os
import paho.mqtt.client as mqtt
import logging
import lgpio  # Import the rpi-lgpio library

# Watermeter stand (will only be used when there is nog meterstand_water.txt file)
counter = 0

# MQTT URL
mqtt_host = os.getenv('MQTT_HOST')
mqtt_port = os.getenv('MQTT_PORT')
mqtt_topic = os.getenv('MQTT_TOPIC')

# Filename for persisting data locally
fileName = "/usr/src/app/config/meterstand_water.txt"

# Pin property (pin 9 is GPIO 21)
gpio_pin = 9

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('watermeter')

logger.info('Script started')

# Open meterstand.txt file and read meterstand
# If meterstand.txt does not exist, it will create the file and add the meterstand of Counter to it
fn = fileName
if os.path.exists(fn):
    with open(fn, "r+") as f:
        inhoud = f.readline()
        a, b, c = inhoud.split()
        counter = int(c)
else:
    with open(fn, "w") as f:
        f.write('meterstand = ' + repr(counter))

# Initialize lgpio
lgpio.gpiochip_open(0)  # Open the GPIO chip (0 is the default chip)
lgpio.gpio_claim_output(gpio_pin, 0)  # Set the pin as input with pull-down

# Callback function for interrupt
def Interrupt(gpio_pin):
    global counter
    logger.info('Callback function called!')
    time.sleep(0.05)  # Filter out false positives from power fluctuations
    if lgpio.gpio_read(gpio_pin) == 0:
        logger.warning('Quitting event handler because this was probably a false positive')
        return

    # Increment the counter
    with open(fn, "r+") as f:
        inbound = f.readline()
        a, b, c = inbound.split()
        counter = int(c) + 1

    # Write counter to file
    with open(fn, 'w') as f:
        f.write('meterstand = ' + repr(counter))

    # Send JSON to MQTT
    try:
        client = mqtt.Client()
        client.connect(mqtt_host, int(mqtt_port), 60)
        client.publish(mqtt_topic, payload=counter, qos=0, retain=False)
        client.disconnect()
        logger.info("Watermeter counter = " + str(counter))
    except Exception as e:
        logger.error("Could not send message to MQTT server: " + str(e))

# Set up the interrupt event
lgpio.gpio_claim_input(gpio_pin)  # Set the pin as input
lgpio.gpio_set_event(gpio_pin, lgpio.RISING_EDGE, Interrupt)  # Set up the rising edge interrupt

try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    lgpio.gpiochip_close(0)  # Close the GPIO chip
    logger.warning("\nBye")
