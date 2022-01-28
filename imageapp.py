from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter as tki
# from tkinter import ttk
from tkinter.messagebox import showerror
from plantcv import plantcv as pcv
import cluster_jordan
import numpy as np
import threading
import datetime
import imutils
import cv2
import os
import math
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
# import board
# import neopixel


class LeafImageApp:
    def __init__(self, vs, outputPath):
        #### LED SETUP #######
        # self.LED_COUNT = 4  # Number of LED pixels.
        # LED_BRIGHTNESS = 0.2  # LED brightness
        # # LED_ORDER = neopixel.RGB  # order of LED colours. May also be RGB, GRBW, or RGBW
        #
        # self.strip = neopixel.NeoPixel(board.D21, self.LED_COUNT, pixel_order=neopixel.GRB)
        # #self.strip.fill((255, 255, 255))
        ###

        #### Drive Setup ####
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)
        self.upload_file_list = []

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
        # Resize window to match screen dimensions without going full screen
        self.w, self.h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (self.w, self.h))
        # Load a stock image to be a place holder for the leaf area measurements
        # load_image = cv2.imread("/home/pi/LightsCameraPlants/test_plant_image.jpg")
        # load_image = cv2.imread("/Users/alexlewis/Desktop/GitHub/LightsCameraPlants/test_plant_image.jpg")
        load_image = cv2.imread("test_plant_image.jpg") # Test if this relative path continues to work
        os.chdir('../')
        self.load_frame = imutils.resize(load_image, width=int(self.w/2.1))
        # setup frames for gui.
        # parent frame to hold all of user buttons
        bottomframe = tki.Frame(self.root)
        bottomframe.pack(side="bottom", fill="both", expand="yes")
        # embedded frame to hold the sliders
        embeddedleftframe = tki.Frame(bottomframe)
        embeddedleftframe.pack(side="left", fill=tki.X, expand="yes")
        # embedded frame to hold buttons
        embeddedrightframe = tki.Frame(bottomframe)
        embeddedrightframe.pack(side="right", fill=tki.X, expand="yes")
        # additional frame within the button frame to hold google drive input boxes
        embeddedrightrightframe = tki.Frame(embeddedrightframe)
        embeddedrightrightframe.pack(side="bottom", fill=tki.X, expand="yes")

        # OpenCV represents images in BGR order; however PIL
        # represents images in RGB order, so we need to swap
        # the channels, then convert to PIL and ImageTk format
        load_image2 = cv2.cvtColor(self.load_frame, cv2.COLOR_BGR2RGB)
        load_image2 = Image.fromarray(load_image2)
        self.load_image2 = ImageTk.PhotoImage(load_image2)

        # create a button, that when pressed, will take the current
        # frame and save it to file
        self.btn = tki.Button(embeddedrightframe, text="2) Save Original Image?",
                            command=self.takeSnapshot, width=int(self.w / 25), height=2, activebackground='green')
                            # Double check active backgroundworks on pi
        self.btn.pack(side="bottom", padx=10, pady=10, fill=tki.X, expand="yes")
        # make button to analyze leaf area
        measure_btn = tki.Button(embeddedrightframe, text="1) Measure Leaf Area", fg='green',
                                 command=self.measureLeafArea, height=2)
        measure_btn.pack(side="bottom", padx=10, pady=10, fill=tki.X, expand="yes")

        # Google Drive boxes to upload output directory path
        sync_button = tki.Button(embeddedrightrightframe, text="3) Sync output directory with Google Drive", fg='black',
                                 command=lambda: self.syncCommand(), height=2)
        sync_button.pack(side="right", padx=10, pady=10, fill=tki.X, expand="yes")
        sync_label = tki.Label(embeddedrightrightframe, text="Google Drive url .../folders/")
        sync_label.pack(side="left", pady=10)
        self.sync_input = tki.Text(embeddedrightrightframe, width=33, height=1, borderwidth=1, relief="raised")
        self.sync_input.pack(side="left", pady=10)


        # make slider for plant threshold
        self.thresh_slider = None
        self.thresh_slider = tki.Scale(embeddedleftframe,
                                from_=1, to=100, length=int(self.w / 2.2),
                                orient="horizontal", fg="black", label="Leaf identification threshold")
        self.thresh_slider.set(80)
        self.thresh_slider.pack(side="bottom", padx=10, pady=10)

        # make scale for light brightness
        self.green_percent = 0
        self.slider = None
        self.slider = tki.Scale(embeddedleftframe, variable=self.green_percent,
                                from_=0, to=100, length=int(self.w / 2.2), troughcolor="green",
                                orient="horizontal", fg="green",
                                label="LED color percent green relative to white")
        self.slider.set(0)
        self.slider.pack(side="bottom", padx=10, pady=10)

        # start a thread that constantly pools the video sensor for the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
        # set a callback to handle when the window is closed
        self.root.wm_title("Plant View")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    def videoLoop(self):
        # This try/except statement is a pretty ugly hack to get around
        # a RunTime error that Tkinter throws due to threading
        try:
            # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                # grab the frame from the video stream and resize it to
                # have a maximum width of 300 pixels
                self.frame = self.vs.read()
                self.frame = imutils.resize(self.frame, width=int(self.w/2.1))

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
                    self.panel2 = tki.Label(image=self.load_image2)
                    self.panel2.image = self.load_image2
                    self.panel2.pack(side="left", padx=10, pady=10)

                # otherwise, simply update the panel
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
                    self.makeGreen(self.slider.get())
        except RuntimeError:   # removed , e:   - AL
            print("[INFO] caught a RuntimeError")

    def measureLeafArea(self):
        # grab the frame from the video stream and resize it to
        self.measure_frame = self.vs.read()
        self.measure_frame = imutils.resize(self.measure_frame, width=int(self.w/2.1))
        thresh = pcv.rgb2gray_hsv(rgb_img=self.measure_frame, channel="h")
        thresh = pcv.gaussian_blur(img=thresh, ksize=(201, 201), sigma_x=0, sigma_y=None)
        thresh = pcv.threshold.binary(gray_img=thresh, threshold=self.thresh_slider.get(),
                                      max_value=325, object_type="light")
        fill = pcv.fill(bin_img=thresh, size=350000)
        dilate = pcv.dilate(gray_img=fill, ksize=120, i=1)
        id_objects, obj_hierarchy = pcv.find_objects(img=self.measure_frame, mask=dilate)
        shape = np.shape(self.measure_frame)
        roi_contour, roi_hierarchy = pcv.roi.rectangle(img=self.measure_frame,
                                                       x=0, y=150, h=(shape[0] / 2) - 150, w=shape[1])
        # gives 4 diff outputs
        # list of objs, hierarchies say object or hole w/i object
        roi_objects, hierarchy, kept_mask, obj_area = pcv.roi_objects(img=self.measure_frame,
                                                                      roi_contour=roi_contour,
                                                                      roi_hierarchy=roi_hierarchy,
                                                                      object_contour=id_objects,
                                                                      obj_hierarchy=obj_hierarchy, roi_type="partial")

        # clustering defined leaves into individual plants using predefined rows/cols
        clusters_i, contours, hierarchies = cluster_jordan.cluster_contours(img=self.measure_frame, roi_objects=roi_objects,
                                                                            roi_obj_hierarchy=hierarchy, nrow=2, ncol=6,
                                                                            show_grid=True)
        # split the clusters into individual images for analysis
        output_path, imgs, masks = cluster_jordan.cluster_contour_splitimg(rgb_img=self.measure_frame,
                                                                           grouped_contour_indexes=clusters_i,
                                                                           contours=contours,
                                                                           hierarchy=hierarchies)
        sus = False
        num_plants = 0
        areas = {}

        for i in range(0, 6):
            pos = 7 - (i + 1)
            if clusters_i[i][0] != None:
                id_objects, obj_hierarchy = pcv.find_objects(img=imgs[num_plants], mask=masks[num_plants])
                obj, mask1 = pcv.object_composition(img=imgs[num_plants], contours=id_objects, hierarchy=obj_hierarchy)
                m = cv2.moments(obj)
                area = m['m00']
                num_plants += 1
                center, expect_r = cv2.minEnclosingCircle(obj)
                r = math.sqrt(area / math.pi)
                leaf_error = False
                if r <= 0.35 * expect_r:
                    leaf_error = True
                    sus = True
                    print(f"warning: there may be an error detecting leaf {pos}")

                areas[pos] = area
            else:
                areas[pos] = 0
        print(areas)
        print(output_path)

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

    def makeGreen(self, green_percent):
        # for i in range(self.LED_COUNT):
        #     self.strip[i] = (255 - int(255*.01*self.slider.get()), 255, 255 - int(255*.01*self.slider.get()))
        # self.strip.fill((255 - int(255*.01*green_percent), int(255*.01*green_percent), 255 - int(255*.01*green_percent)))
        #self.strip.fill((255,255,255))
        #print("green value:", str(int(255*.01*green_percent)), "white value:", str(255 - int(255*.01*green_percent)))
        pass

        # if self.slider is None:
        #     pass
        # else:
        #     print(str(self.slider.get))

    def takeSnapshot(self):
        # grab the current timestamp and use it to construct the
        # output path
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self.outputPath, filename))
        # save the file
        cv2.imwrite(p, self.measure_frame.copy())
        print("[INFO] saved {}".format(filename))

    def syncCommand(self):
        driveID = str(self.sync_input.get(1.0, "end-1c"))
        print("going")
        if len(driveID) == 33:
            file_list = self.drive.ListFile(
                {'q': "'{}' in parents and trashed=false".format(driveID)}).GetList()
            file_list_titles = []
            for file in file_list:
                file_list_titles.append(file['title'])
            for x in os.listdir(self.outputPath):
                if x not in file_list_titles:
                    f = self.drive.CreateFile({'title': x, 'parents': [{'id': driveID}]})
                    f.SetContentFile(os.path.join(self.outputPath, x))
                    f.Upload()
                    print("[UPLOAD INFO] The file {} has been added to google drive".format(x))

                    # Due to a known bug in pydrive if we
                    # don't empty the variable used to
                    # upload the files to Google Drive the
                    # file stays open in memory and causes a
                    # memory leak, therefore preventing its
                    # deletion
                    f = None
        else:
            showerror("ERROR",
                      "Please make sure that you have inputed the 33 charecter Google Drive ID into the text box. \n\n"
                      "EXAMPLE: if your url was https://.../folders/1M1Uz_Dlp6QlVlQfRi8ftzgViss0udwUW\n\n"
                      "Then copy and paste 1M1Uz_Dlp6QlVlQfRi8ftzgViss0udwUW into the entry box")

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()


