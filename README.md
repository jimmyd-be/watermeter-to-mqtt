
# Watermeter to MQTT

  

The script listens to to a signal of a PNP sensor to create and count the water consumption. This can then be shown on a home assistant installation or other tools.

  

## Requirements

- Raspberry pi or equal (with Python3 support)
- MQTT server installed
- 1K and 2K resistors (if you connect it to a raspberry pi)
- a couple of cables
- Inductive proximity sensor (PNP 3 wires) [PNP sensor on Amazon](https://www.amazon.nl/gp/product/B071FR2R85/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&language=en_GB&psc=1)


## Hardware setup

The blue cable of the proximity sensor need to be connected with a GROUND pin of the raspberry pi.
The brown cable of the proximity sennsor need to be connnected to a 5V-pin of the raspberry pi.

For raspberry pi users:  
The raspberry pi doesn't have any 5V input pins because the Pi is operating on a 3.3V basis. Therefor two resistors need to be placed to lower down the voltage. In the image below the 5V is the black cable of the proximity sensor. The 3.3V need to be to the input pin of the Raspberry pi and the GND need to be connected to a GROUND-pin of the raspberry pi.

![5V to 3.3V circuit](https://i1.wp.com/randomnerdtutorials.com/wp-content/uploads/2015/09/voltage-divider-circuit.png?resize=408%2C151&quality=100&strip=all&ssl=1)

For other devices that can handle 5V input:  
The black cable of the proximity sensor need to be connected to a 5V input pin.


## Installation

### Docker installation
```
docker run --name Watermeter \
        --restart always \
        -e MQTT_HOST=192.168.0.250 \
        -e MQTT_PORT=1883 \
        -e MQTT_TOPIC=watermeter \
        -v /home/pi/config/watermeter:/usr/src/app/config \
        --device /dev/bmc \
        --privileged \
        -d lonelobo0070/watermeter_to_mqtt:latest
```



### Manual installation
Download the python file on your system and try to run it using python3 watermeter.py. It is possible you need to install additional python modules. You can do this by calling ```pip3 install <module>```.

The Python script does use following modules:
- RPi.GPIO
- paho.mqtt

To run the script on a regular basis create a cron job for it (sudo contab -e). For example, I have a cronjob that calls the script on boot: ```@reboot python3 /home/pi/watermeter.py > /var/log/cronlog.log 2>&1```.

To run the script in Systemd you need to copy watermeter.service to /etc/systemd/system/watermeter.service. For enableling this ou need to run 

```systemctl daemon-reload && systemctl enable watermeter && systemctl start watermeter --no-block```

The logs of the Systemd service can be found with:
```systemctl status my_daemon```

## Configuration
The script need to be changed to connect to the correct mqtt host. You can do this by changing ```mqtt_host```, ```mqtt_port```, ```mqtt_topic```, ```fileName``` ```Counter``` and ```gpio_pin``` properties in the file.

**fileName**: is the full path to the file where the script persist the current waterstand.  
**gpio_pin**: is the datapin where you connected the black cable on. For more information of the GPIO pins othe Raspberry pi visit [their site](https://www.raspberrypi.org/documentation/usage/gpio/).  
**Counter**: the initial waterstand of the watermeter. WIll only be used once when calling the script for the first time.  
**mqtt_host**: the hostname or IP addres of the MQTT server  
**mqtt_port**: the port where the MQTT server is listening (default 1883)  
**mqtt_topic**: the topic of the mqtt message
