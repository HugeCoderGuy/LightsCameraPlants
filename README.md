# LightsCameraPlants
## Summary:
Included are all of the necessary files to complete automated measurements of leaf area for plants grown in a lab setting. Measurements of the plants are taken in a standardized 3D printed enclosure that eliminates common issues such as glare, camera positioning, and image cropping. This alleviates much of the post-processing required with other automated phenotyping methods and allows the user to identify leaf area measurements in the real-time. The Python file lightsandcamera.py was written to operate on a raspberry pi with neopixels lights and a USB camera.
## Components:
- [Raspberry pi 3b, 4, or 400](https://www.adafruit.com/product/4296)
- [Adafruit NeoPixel Digital RGB LED Strip - Black 30 LED](https://www.adafruit.com/product/1460?length=1) 
- [7" Touchscreen](https://www.adafruit.com/product/2407)
- [HDMI cord](https://www.adafruit.com/product/2197)
- [USB Cord & Power Supply](https://www.adafruit.com/product/1995)
- [USB to micro usb adapter](https://www.adafruit.com/product/2185)
- [SD Card](https://www.adafruit.com/product/2820)
- Keyboard (if you are not using pi 400)
## Setup
1. Download the [Raspberry Pi Imager software](https://www.raspberrypi.com/software/) and setup the pi os on the fresh SD card. Refer to this [video](https://www.youtube.com/watch?v=ntaXWS8Lk34) for additional help setting up the sd card.
2. Place the sd card into the pi and then power it up with the micro usb. Plug the usb to micro usb cable and HDMI into the pi to connect it to the touchscreen display. Keyboard (if not using the pi 400) to the pi to interact with it.
3. Navigate to the terminal screen and enter
```
git clone https://github.com/HugeCoderGuy/LightsCameraPlants.git
```
4. Then enter
```
cd ~/LightsCameraPlants
bash setup1.sh
```
5. After the `setup1.sh` script runs, your pi should restart. Upon restarting, run this in the command line
```
cd ~/LightsCameraPlants
bash setup2.sh
```
6. If all of the test complete properly, run this in the command line following the completion of `setup2.sh`
```
pip install -r requirements.txt
```
7. Plug the usb camera into the pi and test that the software dependencies were installed correctly by running 
```
sudo python3 lightsandcamera.py --output "/home/pi/pictures"
```
Note that the directory in quotes after --output is the output directory. This folder is where images will be saved too and will be the folder that is synced with your google drive (refer to set _ for google drive sync setup). Feel free to change this output directory to correspond with your current project.
