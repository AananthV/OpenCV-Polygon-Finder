import numpy as np
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import tkinter.filedialog as FileDialog
import time
from scanner import Scanner
import urllib.request as ur

def SelectCaptureWebcam():
    global img, cam, camOn
    if camOn:
        _, img = cam.read()
        root.after(30, SelectCaptureWebcam)

def StartCaptureWebcam():
    global cam, camOn, updateOn

    camOn = True
    cam = cv2.VideoCapture(0) #Change this later
    SelectCaptureWebcam()
    if updateOn is False:
        UpdateImage()
        updateOn = True

def StopCaptureWebcam():
    global cam, camOn
    cam.release()
    camOn = False

def WebcamButton():
    global camOn
    if camOn is True:
        StopCaptureWebcam()
    elif camOn is False:
        StartCaptureWebcam()

def SelectCaptureWificam():
    global root, img, url, camOn
    if camOn is True:
        imgResp=ur.urlopen(url.get())
        imgNp=np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img=cv2.imdecode(imgNp, -1)
        root.after(30, SelectCaptureWificam)

def StartCaptureWificam():
    global url, camOn, updateOn, coordinates
    if url.get() == "":
        coordinates.configure(text="Enter URL First!")
        coordinates.text = "Enter URL First!"
        return
    if camOn is False:
        camOn = True
        SelectCaptureWificam()
    if updateOn is False:
        UpdateImage()
        updateOn = True

def StopCaptureWificam():
    global camOn
    camOn = False

def WifiCamButton():
    global camOn
    if camOn is True:
        StopCaptureWificam()
    elif camOn is False:
        StartCaptureWificam()


def SelectImage():
    global img, updateOn

    path = FileDialog.askopenfilename()
    if len(path) > 0:
        img = cv2.imread(path)
        if updateOn is False:
            UpdateImage()
            updateOn = True

def UpdateImage():
    global root, panelA, panelB, threshValue, img, camOn
    scanner = Scanner(img)
    image, edged, _, __ = scanner.preProcessing(threshValue.get())

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = Image.fromarray(image)
    edged = Image.fromarray(edged)

    image = ImageTk.PhotoImage(image)
    edged = ImageTk.PhotoImage(edged)

    if panelA is None or panelB is None:
        panelA = tk.Label(image=image)
        panelA.image = image
        panelA.pack(side="left", padx=10, pady=10)

        panelB = tk.Label(image=edged)
        panelB.image = edged
        panelB.pack(side="right", padx=10, pady=10)

    else:
        panelA.configure(image=image)
        panelB.configure(image=edged)
        panelA.image = image
        panelB.image = edged

    root.after(15, UpdateImage)

def ScanImage():
    global root, coords, coordinates, img, camOn
    if img is not None and camOn is False:
        scanner = Scanner(img)
        coords = scanner.scan(threshValue.get())
        if coords != (5,5):
            coordinates.configure(text="Co-ordinates: "+str(coords))
            coordinates.text = "Co-ordinates: "+str(coords)
        else:
            coordinates.configure(text="Starting Node")
            coordinates.text = "Starting Node"
    else:
        coordinates.configure(text="Select/Capture Image First!")
        coordinates.text = "Select/Capture Image First!"

img = None
coords = None
root = tk.Tk(screenName=None, baseName=None, className=' Co-ordinate Finder', useTk=1)
panelA = None
panelB = None
threshValue = tk.IntVar()
url = tk.StringVar()
camOn = False
updateOn = False
cam = None

scanButton = tk.Button(root, text="Scan Image", command=ScanImage)
scanButton.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

selectFrame = tk.Frame(root)
sbtn = tk.Button(selectFrame, text="Select an Image", command=SelectImage)
cweb = tk.Button(selectFrame, text="Capture (Webcam)", command=WebcamButton)
cwifi = tk.Button(selectFrame, text="Capture (Wifi)", command=WifiCamButton)
cweb.pack(side="left", fill="both", expand="yes", padx=10, pady=10)
cwifi.pack(side="left", fill="both", expand="yes", padx=10, pady=10)
sbtn.pack(side="left", fill="both", expand="yes", padx=10, pady=10)
selectFrame.pack(side="bottom", fill="both", expand="yes", padx=10)


urlFrame = tk.Frame(root)
urlText = tk.Label(urlFrame, text="URL:")
urlEntry = tk.Entry(urlFrame, textvariable=url)
urlText.pack(side="left", padx=10, pady=10)
urlEntry.pack(side="left", fill="both", expand="true", padx=10, pady=10)
urlFrame.pack(side="bottom", fill="both", expand="yes", padx=10)

threshFrame = tk.Frame(root)
threshText = tk.Label(threshFrame, text="Threshold:")
scale = tk.Scale(threshFrame, from_=0, to=255, orient="horizontal", variable=threshValue)
threshText.pack(side="left", padx=10, pady=10)
scale.pack(side="left", fill="both", expand="yes", padx=10, pady=10)
threshFrame.pack(side="bottom", fill="both", expand="yes", padx=10)

coordinates = tk.Label(root, text="Scan to obtain coordinates!")
coordinates.pack(side="bottom", padx=10, pady=10)

root.mainloop()
