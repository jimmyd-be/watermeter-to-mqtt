#!/usr/bin/python
import sys

import lgpio
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
fileName = "/usr/src/app/config/meterstand_water.txt""

# Pin property (pin 9 is GPIO 21)
gpio_pin = 9

# Logging setup
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('watermeter')

logger.info('Script started')

# Open meterstand.txt file and read meterstand
fn = fileName
if os.path.exists(fn):
    with open(fn, "r") as f:
        inhoud = f.readline()
        a, b, c = inhoud.split()
        counter = int(c)
else:
    with open(fn, "w") as f:
        f.write('meterstand = ' + repr(counter))

# Open GPIO chip and configure the pin
chip = lgpio.gpiochip_open(0)  # Open GPIO chip 0
lgpio.gpio_claim_input(chip, gpio_pin)  # Set pin as input

# Callback function for GPIO events
def interrupt(chip, gpio):
    global counter
    logger.info('Callback function called!')
    time.sleep(0.05)  # Filter out false positives
    if lgpio.gpio_read(chip, gpio_pin) == 0:
        logger.warning('Quitting event handler because this was probably a false positive')
        return
    # Increment counter and write to file
    with open(fn, "r") as f:
        inbound = f.readline()
        a, b, c = inbound.split()
        counter = int(c)
    counter += 1
    with open(fn, "w") as f:
        f.write('meterstand = ' + repr(counter))
    # Send JSON to MQTT
    try:
        client = mqtt.Client()
        client.connect(mqtt_host, int(mqtt_port), 60)
        client.publish(mqtt_topic, payload=counter, qos=0, retain=False)
        client.disconnect()
        logger.info("Watermeter counter = " + str(counter))
    except Exception as e:
        logger.error(f"Could not send message to MQTT server: {e}")


# Initialize the previous state
previous_state = lgpio.gpio_read(chip, gpio_pin)

try:
    # Configure the pin for alerts
    lgpio.gpio_claim_alert(chip, gpio_pin, lgpio.BOTH_EDGES)

    while True:
        # Read the current state of the pin
        current_state = lgpio.gpio_read(chip, gpio_pin)

        # Detect a rising edge (transition from LOW to HIGH)
        if previous_state == 0 and current_state == 1:
            interrupt(chip, gpio_pin)  # Call the interrupt function

        # Update the previous state
        previous_state = current_state

        time.sleep(0.01)  # Adjust polling interval as needed
except KeyboardInterrupt:
    lgpio.gpiochip_close(chip)  # Cleanup GPIO
    logger.warning("\nBye")
