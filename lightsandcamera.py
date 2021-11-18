import board
import neopixel
import cv2
from datetime import datetime
import os

#Experiment Parameters:
Experiment_name = "Test"
Experiment_directory = "Pictures" #Directory from home location

# LED strip configuration:
LED_COUNT = 1  # Number of LED pixels.
LED_BRIGHTNESS = 0.2  # LED brightness
LED_ORDER = neopixel.RGB  # order of LED colours. May also be RGB, GRBW, or RGBW
print(dir(board))

strip = neopixel.NeoPixel(board.D12, LED_COUNT, pixel_order=neopixel.RGBW)

strip.fill(( 0, 100, 0))

# Camera setup
cam = cv2.VideoCapture(0)
directory = r'/home/pi/{}'.format(Experiment_directory)
os.chdir(directory)


# Check if the webcam is opened correctly
if not cam.isOpened():
    raise IOError("Cannot open webcam")

cv2.namedWindow("Plant View")

img_counter = 0

while True:
    ret, frame = cam.read()
    
    # dd/mm/YY H:M:S
    now = datetime.now()
    dt_string = now.strftime("Date%d_%m_%Y_Time%H_%M_%S")
    print(dt_string)
    
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("Plant View", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "{}_{}.png".format(Experiment_name, dt_string)
#         img_name = "{}{}.png".format(directory, dt_string)
        print(img_name)
        print("Before saving image:")  
        print(os.listdir(directory))  
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        print("After saving image:")  
        print(os.listdir(directory))
        
        if not cv2.imwrite(img_name, frame):
             raise Exception("Could not write image")
        img_counter += 1

cam.release()

cv2.destroyAllWindows()
