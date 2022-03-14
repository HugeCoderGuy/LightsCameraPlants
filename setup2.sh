#! /bin/sh
ls /dev/i2c* /dev/spi*
python blinkatest.py
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo pip install plantcv
sudo apt-get install libatlas-base-dev
sudo pip3 unistall numpy #trouble shooting purposes
sudo apt install python3-numpy
sudo pip install -U numpy
sudo pip unistall scipy
sudo apt install python3-scipy
