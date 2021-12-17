# import the necessary packages
from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter as tki
import threading
import datetime
import imutils
import cv2
import os


class PhotoBoothApp:
    def __init__(self, vs, outputPath):
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.vs = vs
        self.outputPath = outputPath
        self.frame = None
        self.measure_frame = None
        self.thread = None
        self.stopEvent = None
        # initialize the root window and image panel
        self.root = tki.Tk()
        self.panel = None
        load_image = cv2.imread("/Users/alexlewis/Desktop/GitHub/LightsCameraPlants/test_plant_image.jpg")
        # cv2.imshow("load_image", load_image)
        # cv2.waitKey(0)
        self.load_frame = imutils.resize(load_image, width=300)

        # OpenCV represents images in BGR order; however PIL
        # represents images in RGB order, so we need to swap
        # the channels, then convert to PIL and ImageTk format
        load_image2 = cv2.cvtColor(self.load_frame, cv2.COLOR_BGR2RGB)
        load_image2 = Image.fromarray(load_image2)
        load_image2 = ImageTk.PhotoImage(load_image2)
        self.panel2 = tki.Label(image=load_image2)
        self.panel2.image = load_image2
        self.panel2.pack(side="right", padx=10, pady=10)

        # self.panel2 = None
        self.led_brightness = int(2)
        # create a button, that when pressed, will take the current
        # frame and save it to file
        btn = tki.Button(self.root, text="Save Original Image?",
                         command=self.takeSnapshot)
        btn.pack(side="bottom", fill="both", expand="yes", padx=10,
                 pady=10)
        # make button to analyze leaf area
        measure_btn = tki.Button(self.root, text="Measure Leaf Area",
                                 command=self.measureLeafArea)
        measure_btn.pack(side="bottom", fill="both", expand="yes", padx=10,
                 pady=10)
        # make scale for light brightness
        scale = tki.Scale(self.root, variable=self.led_brightness,
                   from_=100, to=1, length=100,
                   orient="vertical", fg="green")
        scale.pack(side="right", padx=10, pady=10)
        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
        # set a callback to handle when the window is closed
        self.root.wm_title("Plant View")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    def videoLoop(self):
        # DISCLAIMER:
        # I'm not a GUI developer, nor do I even pretend to be. This
        # try/except statement is a pretty ugly hack to get around
        # a RunTime error that Tkinter throws due to threading
        try:
            # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                # grab the frame from the video stream and resize it to
                # have a maximum width of 300 pixels
                self.frame = self.vs.read()
                self.frame = imutils.resize(self.frame, width=300)

                # OpenCV represents images in BGR order; however PIL
                # represents images in RGB order, so we need to swap
                # the channels, then convert to PIL and ImageTk format
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                # if the panel is not None, we need to initialize it
                if self.panel is None:
                    self.panel = tki.Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx=10, pady=10)

                # otherwise, simply update the panel
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
        except RuntimeError:   # removed , e:   - AL
            print("[INFO] caught a RuntimeError")


    def measureLeafArea(self):
        # grab the frame from the video stream and resize it to
        # have a maximum width of 300 pixels
        self.measure_frame = self.vs.read()
        self.measure_frame = imutils.resize(self.measure_frame, width=300)

        # OpenCV represents images in BGR order; however PIL
        # represents images in RGB order, so we need to swap
        # the channels, then convert to PIL and ImageTk format
        image = cv2.cvtColor(self.measure_frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        # if the panel is not None, we need to initialize it
        if self.panel2 is None:
            self.panel2 = tki.Label(image=image)
            self.panel2.image = image
            self.panel2.pack(side="right", padx=10, pady=10)

        # otherwise, simply update the panel
        else:
            self.panel2.configure(image=image)
            self.panel2.image = image


    def takeSnapshot(self):
        # grab the current timestamp and use it to construct the
        # output path
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self.outputPath, filename))
        # save the file
        cv2.imwrite(p, self.frame.copy())
        print("[INFO] saved {}".format(filename))

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()