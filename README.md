# LightsCameraPlants
### Automated Phenotyping hardware/software to assist with real-time data collection and analysis for under $120[^1].
[^1]: The price is roughly $110 if you already own a monitor, keyboard, mouse, hdmi, usb cords and have access to a 3d printer and soldering iron. Otherwise all of the extra gizmoes and gadgets bring the price up to roughly $230.

<p align="center">
<img src="https://user-images.githubusercontent.com/81666253/189248803-91d10dcb-2914-43da-96c0-5be8b8195994.png" width="750">
</p>

## Summary:
Included are all of the necessary files to complete automated measurements of leaf area for plants grown on 100mmx15mm square petri-dishes. Measurements of the plants are taken in a standardized 3D printed enclosure that eliminates common issues such as glare, camera positioning, and image cropping for image analysis. This alleviates much of the post-processing required with other automated phenotyping methods and allows the user to identify leaf area measurements in the real-time. Users that are disinterested in leaf area can still untilize this system for streamlined image collection and image/data transfer to Google Drive[^2]. 
[^2]: Included in the files_to_print folder is a tray to hold your classic petri dish
## Components:
<p align="right" alt="side Text">
<strong>Prototype used to test lighting orientation in housing</strong>
</p>
<img src="https://media.giphy.com/media/Gkp3e25MK1DQDEJu5S/giphy-downsized.gif" alt="side Image" align="right" height="auto"/>

- [Raspberry pi 3b, 4, or 400](https://www.adafruit.com/product/4296)
- [NeoPixel Diffused 8mm Through-Hole LED - 5 Pack](https://www.adafruit.com/product/1734?gclid=EAIaIQobChMI-vbjzefJ9gIV1BatBh1jzA-aEAAYASAAEgI8xfD_BwE) 
- [7" Touchscreen](https://www.adafruit.com/product/2407)
- [HDMI cord](https://www.adafruit.com/product/2197)
- [USB Cord & Power Supply](https://www.adafruit.com/product/1995)
- [USB to micro usb adapter](https://www.adafruit.com/product/2185)
- [SD Card](https://www.adafruit.com/product/2820)
- [Raspberry Pi Camera V2](https://www.raspberrypi.com/products/camera-module-v2/)
- [Heat-set inserts](https://www.adafruit.com/product/4256)
- [M3 Screws](https://www.amazon.com/Sutemribor-320Pcs-Stainless-Button-Assortment/dp/B07CYNKLT2/ref=sr_1_4?keywords=m3+screws&qid=1647405731&sr=8-4)
- [Keyboard and mouse if you want it](https://www.adafruit.com/product/1738)
- 3D Printer Filament (roughly 350g)
- [100mmx15mm Square Petri Dish](https://www.simport.com/en/products/54-d210-16-square-petri-dish-with-grid.html)

<p align="right" alt="side Text">
<strong>Various Prototype Housing Designs</strong>
</p>
<img src="/images/housing_designs.jpg" alt="side Image" align="right" height="auto" width="270"/>

**Tools**
- A 3D printer
- Soldering tools and setup
- [Heat-set insert tip](https://www.adafruit.com/product/4239_)
<br>

## Setup
### Part 1: Hardware
1. Download the raspberry pi case .stl files[^3], housing.stl, tray.stl, and screen_backing.stl files from the files_to_print folder. Use [Cura](https://ultimaker.com/software/ultimaker-cura) to develop a gcode file for your 3D prints of the components. I recommend that you use these settings:
   - 20% infill (I generally use triangles)
   - Normal - .15mm profile for all prints
   - adhesion if printing the display backing or raspberry pi case
   - Matte Black PLA filament for the 3D printer
   - Supports (overhang angle = 80)
2. Sand down the edges of the plant tray so that they are smooth. Slide the tray into the enclosure to ensure that the edges have been smoothed enough.
3. Using the heat-set insert tip with a soldering iron heated to 700F, press heat inserts into the four holes on the back of the enclosure and four holes on the display backing. 
<img src="/images/backplate.jpg" width="200" alt="side Image" align="right">

4. Attach the touchscreen to the display backing using x4 M3x8mm screws
5. slide the display backing into the the enclosure slot. Sandpaper down the interfaces if the connection is rough.
6. Connect the pi camera through the lid of the raspberry pi case. Then seal the case with x4 M3x16mm screws. They should screw right into the plastic.
7. Screw the raspberry pi and its case onto the back of the enclosure into the x4 inserts using x4 M3x8mm
8. Slide the backplate onto the main housing and ensure that the touchscreen has a snug fit with the backplate
9. Slide a piece of paper with letters into the tray position. Using the white ring that comes with the picamera, adjust the focus of the picamera until the image is roughly sharp enough to read the letters.
10. Slide the picam into the slot at the top of the enclosure so that the top of the camera is flush with the slot. Then use electrical tape to hold the camera in place. WARNING: Do not use any other tape other than electrical tape. The camera is incredibly sensitive to static electricity and will break if scotch tape is applied to the back of the camera.
11. solder neopixels together in a chain with 3 wires that have pin connectors for data, voltage, and ground. Be mindful how how long the wires are between each neopixel to ensure that they reach each of the holes. Refer to the image below for what each prong of the neopixel is used for
12. Connect the ground cable to the ground pin, the Vin cable to the 5V pin, and the data in line to GPIO21. Please refer to [online documentation](https:includelineheree) for the specific pinout of your raspberry pi model. An example pinout of the pi3b is shown below with arrows referring to the correct pins.

<p align="center">
<img src="/images/pi3b_pins.jpg" width="400">
<img src="/images/neopixel_prongs.jpg" width="300">

</p>

[^3]: Credits for the raspberry pi case file can be given to [0110-M-P on Thingiverse](https://www.thingiverse.com/thing:922740/files)

### Part 2: Software
1. Download the [Raspberry Pi Imager software](https://www.raspberrypi.com/software/) and setup the pi os on the fresh SD card. Refer to this [video](https://www.youtube.com/watch?v=ntaXWS8Lk34) for additional help setting up the sd card.
2. Place the sd card into the pi and then power it up with the micro usb. Plug the usb to micro usb cable and HDMI into the pi to connect it to the touchscreen display. Keyboard (if not using the pi 400) to the pi to interact with it.
3. Connect your pi to wifi. Without wifi you will not be able to operate the software or download the system dependencies. 
3. in the terminal, run `sudo raspi-config`, then click Interface Options followed by Legacy Camera. Finally enable the camera and then click finish. You will likely have to reboot the pi. Note that if you are using a pi 3b, enabling the legacy camera will likely reduce the usable screen size on the 7" display due to the new driver for the pi 4.
4. Navigate to the terminal screen and enter
```
git clone https://github.com/HugeCoderGuy/LightsCameraPlants.git
```
4. Then enter
```
cd ~/LightsCameraPlants
bash setup1.sh
```
When prompted, type Y followed by enter to continue throughout the installation. Make sure that you do not allow the pi to sleep while setup1.sh is running. If the pi sleeps or crashes, you can either try rerunning the script on reboot or re-flashing the SD card and trying again. The terminal may also prompt you to run `sudo dpkg --configure -a`. If so, do so and rerun the script or just `sudo python raspi-blinka.py` if the code got stuck on the blinka script. 
6. After the `setup1.sh` script runs, your pi should restart. Upon restarting, run this in the command line
```
cd ~/LightsCameraPlants
bash setup2.sh
```
7. Plug the usb camera into the pi and test that the software dependencies were installed correctly by running 
```
sudo python3 lightsandcamera.py -o /home/pi/Pictures -p 1
``` 
   Note that the directory in quotes after -o is the output directory. This folder is where images will be saved too and will be the folder that is synced with your google drive (refer to step 8 for google drive sync setup). Feel free to change this output directory to correspond to a folder with your current project.
   
8. **Setting up Google Drive Sync Functionality**
   1. LightsCameraPlants allows you to sync your output directory with a google drive folder to allow for easy documentation of samples. To do this you must first get authentication for Google Service API. Refer to [this PDF](https://d35mpxyw7m7k7g.cloudfront.net/bigdata_1/Get+Authentication+for+Google+Service+API+.pdf) for documentation on how to setup your authentication. 
   2. After downloading your credentials file. Copy and paste your client_id and client_secret without quotes into the `settings_to_be_edited.yaml` file in your LightsCameraPlants folder.
   3. Finally rename the `settings_to_be_edited.yaml` to `settings.yaml`. Make sure you do not accidentally share your client_id and client_secret.

## User Guide
1. After powering up the pi and plugging in all of the necessary hardware, navigate to the terminal and type
```
cd ~/LightsCameraPlants/
```
followed by
```
sudo python3 lightsandcamera.py -o /home/pi/Pictures -p 1
```
As stated previously, the /home/pi/Pictures call refers to the output directory that can be changed by creating a new folder, navigating to it in the terminal and then typing `pwd`, then copy/pasting that directory after the --output argument call.

**Other Arguments You can Call:**

*Airplane Mode*: To use the system in a location without wifi, at the cost of the google drive upload feature, you can put the system in airplane mode by calling
```
sudo python3 lightsandcamera.py -o /home/pi/Pictures --airplaneMode True
```
or 
```
sudo python3 lightsandcamera.py -o /home/pi/Pictures -a True
```
*Pi Camera*: If you want to use an usb camera rather than picamera, call
```
sudo python3 lightsandcamera.py -o /home/pi/Pictures
```
Note that you can call both of the --airplaneMode and --picamera args in the same statement.

2. Right click the link that appears in the terminal after the "warming up camera..." statement and then click "Open URL". If you are just using the touchscreen, copy and paste the link into chromium
   - If you are currently unable to connect to wifi and do not need the drive features, recall that you can add the `-a True` argument to the script call which activates airplane mode
3. Sign into your appropriate google account and allow the api to access your drive

Insert Photo here of GUI
4. Buttons and Functions
   - A: The LED Slider allows you to change the hue of the Neopixel lights. 0% is pure white light and 100% is pure green light. This functionality is meant to assist with the software's identification of leaf area if needed.
   - B: The Threshold slider defines how the software identifies the leaves. A lower threshold is more inclusive of potential leaf measurements while a higher threshold is exclusive. Note that minor changes in the threshold can have major affects on leaf identification error.
   - C: "Measure Leaf Area" button takes the current image from the live feed and processes the image to find leaf area. The final displayed image on the right shows the regions of identified leaf area. If the leaf area is not identified, alter the threshold or LED hue to help the system recognize leaf area.
   - D: If the processed image on the right has appropriately identified the leaf area in the sample, click the "save image" button to save the original snapshot without the leaf outlines. The associated leaf area measurements will be stored in the "Data" folder in a .csv titled with the date of the measurements. The image and measurements will be saved to the output directory called in `sudo python3 lightsandcamera.py "-o INSERT_OUTPUT_DIRECTORY_HERE"`.
   - E: Once you are done collecting samples sync the output directory content with a Google Drive by inserting the drive ID into box E_1. The drive ID is the series of numbers at the end of the URL for that google drive folder. Then click the "sync output directory with Google Drive" button to automatically upload all of your data to the cloud.
    - For example, if your google drive folder has the url "https://drive.google.com/drive/u/0/folders/1M1Uz_Dlx6QlVlQfRi8ftzgViss0udwUW", copy and paste the last bit, 1M1Uz_Dlx6QlVlQfRi8ftzgViss0udwUW into the text box.
5. Closing the program can be done by clicking the x in the upper right corner or typing ctr+c once or twice into the terminal.

<br><br>
<strong>Acknowledgements</strong>

This project was done for and funded by the UC Davis Bloom Lab. Huge thanks goes out to Arnold Bloom for accepting me into his lab, [Jordan Stefani](https://github.com/massivejords) for providing the code that assist with leaf area analysis, and [Anna Knapp](https://github.com/AnnaKnapp) for providing me with essential mentorship as I became familiar with the Raspberry Pi platform and its integration with the numerous python libraries.
