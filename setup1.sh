#! /bin/sh
sudo apt-get install python-pip
Y
sudo pip install --upgrade setuptools
sudo apt full-upgrade
sudo apt clean
cd ~
sudo pip install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python raspi-blinka.py
