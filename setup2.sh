#! /bin/sh
ls /dev/i2c* /dev/spi*
python blinkatest.py
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel