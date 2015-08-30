# RPi-Display
12864 OLED display library for Raspberry Pi

## Software setup

### Enable SPI on Raspberry Pi

remove the blacklisting for `spi-bcm2708` in `/etc/modprobe.d/raspi-blacklist.conf`

reboot or load the driver manually with `sudo modprobe spi-bcm2708`

### Install spidev module

Checkout [Python Spidev](https://github.com/doceme/py-spidev)

### Install other requirements

#### RPi.GPIO

for basic Raspberry Pi GPIO manipulation

`sudo apt-get install python-rpi.gpio`

#### bdflib

for working with BDF font files

`pip install bdflib`

#### zerorpc

for remote display control

`pip install zerorpc`

## Hardware setup

| OLED Display  | Raspberry Pi  |
| ------------- | ------------- |
| GND           | PIN 25 (GND)  |
| VCC           | PIN 1  (3.3V) |
| D0            | PIN 23 (SCLK) |
| D1            | PIN 19 (MOSI) |
| RST           | PIN 13        |
| DC            | PIN 15        |

![](http://elinux.org/images/8/80/Pi-GPIO-header-26-sm.png)

## Usage

```python
from display import Display

disp = Display(15, 13, "/home/pi/wenquanyi_12pt.bdf")
disp.displayText(0, 0, 1, "Hello World")
```
### Remote display control over zerorpc

Run server script:

`python server.py`

Display text via rpc

`zerorpc "tcp://IP-ADDRESS:4242" displayText 0 0 1 "Hello World"`

Show current time via rpc

`./showtime.sh`
