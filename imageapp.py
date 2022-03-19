from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter as tki
from tkinter.messagebox import showerror
from plantcv import plantcv as pcv
import cluster_jordan
import numpy as np
import threading
import datetime
import imutils
import csv
import cv2
import os
import math
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import board
import neopixel


# Note to self: use [pipreqs .] to make requirements.txt file for dependencies


class LeafImageApp:
    def __init__(self, vs, picamera_arg, outputPath, airplaneMode):
        # LED setup
        self.LED_COUNT = 4  # Number of LED pixels.

        self.strip = neopixel.NeoPixel(board.D21, self.LED_COUNT, brightness = .2, pixel_order=neopixel.RGB)
        self.strip.fill((255, 255, 255))

        # Google Drive setup if not in airplane mode
        self.airplaneMode = airplaneMode
        if not self.airplaneMode:
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            self.drive = GoogleDrive(gauth)

        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.vs = vs
        # If picamera is being used, capture image with picam command rather than video stream for better image quality
        self.picamera_arg = picamera_arg
        # Output path occasionally saves incorrectly on Pi. Dealing with that here.
        if outputPath[0] == " ":
            self.outputPath = outputPath[1:len(outputPath)]
        else:
            self.outputPath = outputPath
        self.frame = None
        self.measure_frame = None
        self.thread = None
        self.stopEvent = None

        # initialize .csv file for leaf area data
        csv_ts = datetime.datetime.now()
        csv_filename = "leaf_areas_{}.csv".format(csv_ts.strftime("%m-%d-%Y"))
        self.csv_folder = os.path.join(self.outputPath, "Data")
        self.csv_p = os.path.sep.join((self.csv_folder, csv_filename))
        if not os.path.exists(self.csv_folder):
            os.mkdir(self.csv_folder)
        if not os.path.exists(self.csv_p):
            header = ['Timestamp', 'Leaf 1 (mm)', 'Leaf 2 (mm)', 'Leaf 3 (mm)', 'Leaf 4 (mm)', 'Leaf 5 (mm)',
                      'Leaf 6 (mm)', "Potential Errors with Leaf #s"]
            with open(self.csv_p, 'w', newline='') as f:
                writer = csv.writer(f)
                # write the header
                writer.writerow(header)

        # initialize the root window and image panel
        self.root = tki.Tk()
        self.panel = None
        # Resize window by saving users window width and height
        # to match screen dimensions without going full screen
        self.w, self.h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (self.w, self.h))
        # Load a stock image to be a place holder for the leaf area measurements
        # load_image = cv2.imread("/home/pi/LightsCameraPlants/test_plant_image.jpg")
        load_image = cv2.imread("startup_image.png") # Test if this relative path continues to work
        os.chdir('../')
        self.load_frame = imutils.resize(load_image, width=int(self.w/2.1), height=int(self.h/3))
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
        self.save_button = tki.Button(embeddedrightframe, text="2) Save Original Image?", command=self.takeSnapshot,
                                      width=int(self.w / 25), height=2, activebackground='green')
                                      # Double check active backgroundworks on pi
        self.save_button.pack(side="bottom", fill=tki.X, expand="yes") # , padx=10 pady=10
        # make button to analyze leaf area
        measure_btn = tki.Button(embeddedrightframe, text="1) Measure Leaf Area", fg='green',
                                 command=self.measureLeafArea, height=2)
        measure_btn.pack(side="bottom", fill=tki.X, expand="yes") # , padx=10 pady=10

        # Google Drive boxes to upload output directory path that changes based on the airplane mode setting
        # airplaneMode off
        if not self.airplaneMode:
            sync_button = tki.Button(embeddedrightrightframe, text="Sync",
                                     fg='black', command=lambda: self.syncCommand(), height=2)
            sync_button.pack(side="right", pady=10, fill=tki.X, expand="yes") # , padx=10
            sync_label = tki.Label(embeddedrightrightframe, text="Drive url .../folders/")
            sync_label.pack(side="left") #, pady=10)
            self.sync_input = tki.Text(embeddedrightrightframe, width=33, height=1, borderwidth=1, relief="raised")
            self.sync_input.pack(side="left", pady=10)
        # airplaneMode on: removes self.syncCommand()
        else:
            sync_button = tki.Button(embeddedrightrightframe, text="[AIRPLANE MODE] Unable to Sync",
                                     fg='black', bg="red", height=2)
            sync_button.pack(side="right", fill=tki.X, expand="yes")  # , padx=10 pady=10,
            sync_label = tki.Label(embeddedrightrightframe, text="Drive url .../folders/")
            sync_label.pack(side="left") # pady=10
            self.sync_input = tki.Text(embeddedrightrightframe, width=33, height=1, borderwidth=1, relief="raised")
            self.sync_input.pack(side="left") # pady=10

        # make slider for plant threshold
        self.thresh_slider = None
        self.thresh_slider = tki.Scale(embeddedleftframe,
                                from_=1, to=130, length=int(self.w / 4),
                                orient="horizontal", fg="black", label="Identification threshold")
        self.thresh_slider.set(80)
        self.thresh_slider.pack(side="bottom", pady=10) # , padx=10

        # make scale for light brightness
        self.green_percent = 0
        self.slider = None
        self.slider = tki.Scale(embeddedleftframe, variable=self.green_percent,
                                from_=0, to=100, length=int(self.w / 4), troughcolor="green",
                                orient="horizontal", fg="green",
                                label="LED green hue")
        self.slider.set(30)
        self.slider.pack(side="bottom", pady=10) #  padx=10

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
                self.frame = self.vs.read()
                self.oFrame = self.frame
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
                    self.panel.pack(side="left", pady=10, padx=5)
                    self.panel2 = tki.Label(image=self.load_image2)
                    self.panel2.image = self.load_image2
                    self.panel2.pack(side="left", pady=10, padx=5)

                # otherwise, simply update the panel
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
                    self.makeGreen(self.slider.get())
        except RuntimeError:   # removed , e:   - AL
            print("[INFO] caught a RuntimeError")

    def measureLeafArea(self):
        # This function takes a snapshot of the video feed and displays it in the second panel
        # with coloring to indicate the software's identified leaf area
        self.measure_frame = self.vs.read()
        image = self.measure_frame
        self.measure_frame = imutils.resize(self.measure_frame, width=int(self.w/2.1))

        # Processing code
        shape = np.shape(image)
        img = pcv.crop(img=image, x=320, y=100, h=600, w=590)

        b = pcv.rgb2gray_lab(rgb_img=img, channel="b")
        avg = np.average(img)
        print(avg)
        std = np.std(img)
        if avg > 220 and std < 25:
            b = pcv.hist_equalization(b)
            t = 100
        else:
            t = 140
        b_thresh = pcv.threshold.binary(gray_img=b, threshold=t - 6, max_value=255, object_type="light")
        bsa_fill1 = pcv.fill(bin_img=b_thresh, size=300)
        bsa_fill1 = pcv.closing(gray_img=bsa_fill1)
        bsa_fill1 = pcv.erode(gray_img=bsa_fill1, ksize=3, i=1)
        bsa_fill1 = pcv.dilate(gray_img=bsa_fill1, ksize=3, i=1)
        bsa_fill1 = pcv.fill(bin_img=bsa_fill1, size=300)
        print(type(bsa_fill1))

        id_objects, obj_hierarchy = pcv.find_objects(img=img, mask=bsa_fill1)

        shape = np.shape(img)
        roi_contour, roi_hierarchy = pcv.roi.rectangle(img=img, x=0, y=0, h=shape[0] / 2, w=shape[1])

        # gives 4 diff outputs
        # list of objs, hierarchies say object or hole w/i object
        roi_objects, hierarchy, kept_mask, obj_area = pcv.roi_objects(img=img,
                                                                      roi_contour=roi_contour,
                                                                      roi_hierarchy=roi_hierarchy,
                                                                      object_contour=id_objects,
                                                                      obj_hierarchy=obj_hierarchy, roi_type="partial")

        # clustering defined leaves into individual plants using predefined rows/cols
        clusters_i, contours, hierarchies = cluster_jordan.cluster_contours(img=img, roi_objects=roi_objects,
                                                                            roi_obj_hierarchy=hierarchy, nrow=2, ncol=6,
                                                                            show_grid=True)
        print(type(clusters_i), type(contours), type(hierarchies))
        # split the clusters into individual images for analysis
        output_path, imgs, masks = cluster_jordan.cluster_contour_splitimg(rgb_img=img,
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



        # OpenCV represents images in BGR order; however PIL
        # represents images in RGB order, so we need to swap
        # the channels, then convert to PIL and ImageTk format
        #image = cv2.cvtColor(self.measure_frame, cv2.COLOR_BGR2RGB)
        image = cv2.cvtColor(self.measure_frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(bsa_fill1, mode="1") # ,mode="1"
        image = ImageTk.PhotoImage(image)

        # if the panel is not None, we need to initialize it
        if self.panel2 is None:
            self.panel2 = tki.Label(image=image)
            self.panel2.image = image
            self.panel2.pack(side="right", pady=10) # , padx=10

        # otherwise, simply update the panel
        else:
            self.panel2.configure(image=image)
            self.panel2.image = image

    def makeGreen(self, green_percent):
        # Using the GUI, adjust the hue of the neopixels to support leaf identification
        self.strip.fill((255 - int(255*.01*self.slider.get()), 255, 255 - int(255*.01*self.slider.get())))

        # include pass statement for further testing on macbook
        pass

    def takeSnapshot(self):
        # grab the current timestamp and use it to construct the output path
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%m-%d-%Y_%H-%M-%S"))
        p = os.path.sep.join((self.outputPath, filename))
        # save the file
        cv2.imwrite(p, self.omeasure_frame.copy())
        print("[INFO] saved {}".format(filename))

        # Save leaf area data to .csv for that day
        csv_timestamp = "{}".format(ts.strftime("%m/%d/%Y %H:%M:%S"))
        data = [csv_timestamp]
        for i in range(1, 7):
            data.append(self.areas.get(i))
        data.append(self.print_error)
        print(data)
        with open(self.csv_p, 'a', newline='') as f:
            writer = csv.writer(f)
            # write the header
            writer.writerow(data)

    def syncCommand(self):
        # Take the input for Drive ID and then upload all unique images from output directory to that google drive
        driveID = str(self.sync_input.get(1.0, "end-1c"))
        file_metadata = {
            'title': 'Data',
            'parents': [{'id': driveID}],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        # initialize path to child Data folder in output path
        data_path = os.path.join(self.outputPath, 'Data')
        # Assumes that drive inputs are standardized at 33 characters long
        if len(driveID) == 33:
            # make instance of all files in drive folder
            file_list = self.drive.ListFile(
                {'q': "'{}' in parents and trashed=false".format(driveID)}).GetList()
            file_list_titles = {}
            data_list_titles = {}
            # Document all of the files in the drive to prevent duplicate uploads to the drive
            for file in file_list:
                file_list_titles.update({file['title']: file['id']})
            # Repeat for all files in the Data folder
            data_file_list = self.drive.ListFile(
                {'q': "'{}' in parents and trashed=false".format(file_list_titles['Data'])}).GetList()
            for file in data_file_list:
                data_list_titles.update({file['title']: file['id']})
            # Create a child folder called Data to store collected Data
            if "Data" not in file_list_titles:
                data_folder = self.drive.CreateFile(file_metadata)
                data_folder.Upload()
            # Upload all images to the google drive while avoiding duplicates
            for x in os.listdir(self.outputPath):
                if x not in file_list_titles and x != "Data" and x != '.DS_Store':
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
            # Upload all of the .csv files with data to the Data child folder in Drive
            for x in os.listdir(data_path):
                if x != ".DS_Store":
                    # If the file is already in the drive, delete it and then reupload the most recent version
                    if x in data_list_titles:
                        # Initialize GoogleDriveFile instance with file id.
                        file_to_delete = self.drive.CreateFile({'id': data_list_titles[x]})
                        # Delete that file
                        file_to_delete.Trash()  # Move file to trash.
                        f = self.drive.CreateFile({'title': x, 'parents': [{'id': file_list_titles['Data']}]})
                        f.SetContentFile(os.path.join(data_path, x))
                        f.Upload()
                        print("[UPLOAD INFO] The file {} has been added to google drive".format(x))

                        # Due to a known bug in pydrive if we
                        # don't empty the variable used to
                        # upload the files to Google Drive the
                        # file stays open in memory and causes a
                        # memory leak, therefore preventing its
                        # deletion
                        f = None
                    # If the .csv is not in drive Data folder, upload it.
                    else:
                        f = self.drive.CreateFile({'title': x, 'parents': [{'id': file_list_titles['Data']}]})
                        f.SetContentFile(os.path.join(data_path, x))
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
                      "Please make sure that you have inputed the 33 character Google Drive ID into the text box. \n\n"
                      "EXAMPLE: if your url was https://.../folders/1M1Uz_Dlp6QlVlQfRi8ftzgViss0udwUW\n\n"
                      "Then copy and paste 1M1Uz_Dlp6QlVlQfRi8ftzgViss0udwUW into the entry box")


    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()
