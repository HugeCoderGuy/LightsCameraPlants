# LightsCameraPlants
### Automated Phenotyping hardware/software to assist with real-time data collection and analysis for under $100[^1].
[^1]: The price is roughly $90 if you already own a moniter, keyboard, mouse, usb cords and have access to a 3d printer. Otherwise expected cost is roughly $200
## Summary:
Included are all of the necessary files to complete automated measurements of leaf area for plants grown on (insert deimensions) square petri dishs. Measurements of the plants are taken in a standardized 3D printed enclosure that eliminates common issues such as glare, camera positioning, and image cropping for image analysis. This alleviates much of the post-processing required with other automated phenotyping methods and allows the user to identify leaf area measurements in the real-time. This setup can also be used with standard LEDs and standard petri dishes for consistent image collection without leaf area measurements. 
## Components:
- [Raspberry pi 3b, 4, or 400](https://www.adafruit.com/product/4296)
- [Adafruit NeoPixel Digital RGB LED Strip - Black 30 LED](https://www.adafruit.com/product/1460?length=1) 
- [7" Touchscreen](https://www.adafruit.com/product/2407)
- [HDMI cord](https://www.adafruit.com/product/2197)
- [USB Cord & Power Supply](https://www.adafruit.com/product/1995)
- [USB to micro usb adapter](https://www.adafruit.com/product/2185)
- [SD Card](https://www.adafruit.com/product/2820)
- USB Camera or Pi Camera
- Keyboard (if you are not using pi 400)
- [this guy?](https://www.adafruit.com/product/1738)

**Tools**
- A 3D printer with a print plate of at least somethingxsomething and height of mm.
- Soldering tools and setup

## Setup
### Part 1: Hardware
1. Download the housing.stl, tray.stl, and screen_backing.stl files from the files_to_print folder. Use [Cura](https://ultimaker.com/software/ultimaker-cura) to develop a gcode file for your 3D prints of the components. I recommend that you use these settings:
   - 20% infill
   - Nozzel fill
   - No adhesion
   - Matte Black PLA filament for the 3D printer
   - .175mm (Normal) profile for the Housing
   - .1313mm (Fine) profile for the plate and touchscreen backboard
2. Attach the touchscreen to the backplate using x4 ___ and x4 ____
3. Slide the backplate onto the main housing and ensure that the touchscreen has a snug fit with the backplate
4. Connect camera to the housing
5. solder neopixels?
6. Connect the ground cable to pin 1, the Vin cable to pin 2, and the data in line to pin 3. Please refer to [online documentation](https:includelineheree) for the specific pinout of your raspberry pi model. Please note that each of these pin numbers refer to the GPIO number which do not follow the cronological ordering from 1-40.
7. 
### Part 2: Software
1. Download the [Raspberry Pi Imager software](https://www.raspberrypi.com/software/) and setup the pi os on the fresh SD card. Refer to this [video](https://www.youtube.com/watch?v=ntaXWS8Lk34) for additional help setting up the sd card.
2. Place the sd card into the pi and then power it up with the micro usb. Plug the usb to micro usb cable and HDMI into the pi to connect it to the touchscreen display. Keyboard (if not using the pi 400) to the pi to interact with it.
3. Connect your pi to wifi. Without wifi you will not be able to operate the software or download the system dependencies. 
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
sudo python3 lightsandcamera.py "-o /home/pi/Pictures"
``` 
   - Note that the directory in quotes after -o is the output directory. This folder is where images will be saved too and will be the folder that is synced with your google drive (refer to step 8 for google drive sync setup). Feel free to change this output directory to correspond to a folder with your current project.
8. **Setting up Google Drive Sync**
   1. LightsCameraPlants allows you to sync your output directory with a google drive folder to allow for easy documentation of samples. To do this you must first get authentication for Google Service API. Refer to [this PDF](https://d35mpxyw7m7k7g.cloudfront.net/bigdata_1/Get+Authentication+for+Google+Service+API+.pdf) for documentation on how to setup your authentication.  ... install pydrive?
   2. After downloading your credentials file. Copy and paste your client_id and client_secret without quotes into the `settings.yaml` file in your LightsCameraPlants folder.
## User Guide
1. After powering up the pi and plugging in all of the necessary hardware, navigate to the terminal and type
```
cd ~/LightsCameraPlants/
```
followed by
```
sudo python3 lightsandcamera.py "-o /home/pi/Pictures"
```
As stated previously, the /home/pi/Pictures call refers to the output directory that can be changed by creating a new folder, navigating to it in the terminal and then typing `pwd`, then copy/pasting that directory after the --output argument call.
2. Right click the link that appears in the terminal after the "warming up camera..." statement and then click "Open URL". If you are just using the touchscreen, copy and paste the link into chromium
3. Sign into your appropriate google account and allow the api to access your drive

Insert Photo here of GUI
4. Buttons and Functions
   - A: The LED Slider allows you to change the hue of the Neopixel lights. 0% is pure white light and 100% is pure green light. This functionality is meant to assist with the software's identification of leaf area if needed.
   - B: The Threshold slider defines leaf area measuring software's cutoff point for what is or is not a leaf. A lower threshold is more inclusive of potential leaf measurements while a higher threshold is exclusive.
   - C: "Measure Leaf Area" button takes the current image from the live feed and processes the image to find leaf area. The final displayed image on the right shows the regions of identified leaf area. If the leaf area is not identified, alter the threshold or LED hue to help the system recognize leaf area.
   - D: If the processed image on the right has appropriately identified the leaf area in the sample, click the "save image" button to save the original snapshot without the leaf outlines. The associated leaf area measurements will be stored in the "Data" folder in a .csv titled with the date of the measurements. The image and measurements will be saved to the output directory called in `sudo python3 lightsandcamera.py "-o INSERT_OUTPUT_DIRECTORY_HERE"`.
   - E: Once you are done collecting samples sync the output directory content with a Google Drive by inserting the drive ID into box E_1. The drive ID is the series of numbers at the end of the URL for that google drive folder. Then click the "sync output directory with Google Drive" button to automatically upload all of your data to the cloud.
    - For example, if your google drive folder has the url "https://drive.google.com/drive/u/0/folders/1M1Uz_Dlx6QlVlQfRi8ftzgViss0udwUW", copy and paste the last bit, 1M1Uz_Dlx6QlVlQfRi8ftzgViss0udwUW into the text box.
5. Closing the program can be done by clicking the x in the upper right corner or typing ctr+c once or twice into the terminal.

**Other Arguments You can Call:**
- Airplane Mode: To use the system in a location without wifi, at the cost of the google drive upload feature, you can put the system in airplane mode by calling
```
sudo python3 lightsandcamera.py "-o /home/pi/Pictures" --airplaneMode True
```
- Pi Camera: If you want to use a Raspberry Pi camera instead of a usb camera, call 
```
sudo python3 lightsandcamera.py "-o /home/pi/Pictures" --picamera 1
```
Note that you can call both of the --airplaneMode and --picamera args in the same statement.

<!--##Acknowledgements
This project was done for and funded by the UC Davis Bloom Lab. Huge thanks goes out to Arnold Bloom for accepting me into his lab, Jordan Stefani for providing the code that assist with leaf area analysis, and Anna Knapp for providing me with essential mentorship as I became familiar with the Raspberry Pi platform and its integration with the numerous python libraries. -->


## Appendix: Using System Exclusively for Image Collection
If you are intending to collect image samples of specimen that are not green and in INSERT_DIMENSIONS square petri dishes, print the agar_plate_holder.stl file with the previously defined Cura settings.