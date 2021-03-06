from __future__ import print_function
from imageapp import *
from imutils.video import VideoStream
import argparse
import time


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
	help="path to output directory to store snapshots")
ap.add_argument("-p", "--picamera", type=int, default=-1,
	help="whether or not the Raspberry Pi camera should be used")
ap.add_argument("-a", "--airplaneMode", type=bool, default=False,
	help="increases system ease of use at the cost of leaf area measurements")
args = vars(ap.parse_args())

# initialize the video stream and allow the camera sensor to warmup
print("[INFO] warming up camera...")

vs = VideoStream(usePiCamera=args["picamera"] > 0, resolution=(1280, 720), framerate=16).start()
time.sleep(2.0)

# start the app
pba = LeafImageApp(vs, args["output"], args["airplaneMode"])
pba.root.mainloop()

