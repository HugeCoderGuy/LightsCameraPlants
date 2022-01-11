from __future__ import print_function
from imageapp import *
from cluster_jordan import *
from imutils.video import VideoStream
import argparse
import time
import cv2



# LED strip configuration:
LED_COUNT = 4  # Number of LED pixels.
LED_BRIGHTNESS = 0.2  # LED brightness
#LED_ORDER = neopixel.RGB  # order of LED colours. May also be RGB, GRBW, or RGBW


#strip = neopixel.NeoPixel(board.D21, LED_COUNT, pixel_order=neopixel.RGBW)

#strip.fill(0, 0, 0, 255)

##################################################################################
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
	help="path to output directory to store snapshots")
ap.add_argument("-p", "--picamera", type=int, default=-1,
	help="whether or not the Raspberry Pi camera should be used")
args = vars(ap.parse_args())
# initialize the video stream and allow the camera sensor to warmup
print("[INFO] warming up camera...")
vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
time.sleep(2.0)
# start the app
pba = LeafImageApp(vs, args["output"])
# pba = LeafImageApp(vs, "/Users/alexlewis/Downloads")
pba.root.mainloop()

