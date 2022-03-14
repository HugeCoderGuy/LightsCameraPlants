#! /bin/sh
sudo apt-get install python-pip
sudo pip install --upgrade setuptools
sudo apt full-upgrade
sudo apt clean
cd ~
# install packages
sudo pip install numpy
sudo apt update
sudo apt install python3-opencv
sudo pip install plantcv
sudo pip install board
sudo pip install imutils
sudo pip install Pillow
sudo pip install PyDrive
sudo pip install pydrive
# install adafruit packages
sudo pip install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python raspi-blinka.py
