
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.core.mail import EmailMessage
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import threading
import cv2 as cv
import numpy as np
from cv2 import aruco
import os
import uuid
from multiprocessing import Process
from django.core.files.storage import default_storage
from django.contrib import messages
from twilio.rest import Client
from django.conf import settings


marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
cap = cv.VideoCapture(0)

marker_paramters = aruco.DetectorParameters()
marker_detector = aruco.ArucoDetector(marker_dict, marker_paramters)
MARKER_SIZE = 400 # pix
# to do: create a uuid and match


### Twilio
twilio_sid = settings.TWILIO_SID
twilio_auth = settings.TWILIO_AUTH
twilio_service = settings.TWILIO_SERVICES
client = Client(twilio_sid,twilio_auth)

v = False



def verification():
    
    message = client.messages.create(
    body='Authorize? Y/N',
    from_='+18552248052',
    to='+18187978710'
    )
    messagefrom = client.messages.list(from_='+18187978710', to='+18552248052')
    for r in messagefrom:
        client.messages(r.sid).delete()
    verification.__func_code__ = (lambda:None).__code__
    


def createmarkers(numpics):
    for id in range(numpics):
        marker_image = aruco.generateImageMarker(marker_dict, id, MARKER_SIZE)
        #cv.imshow('img', marker_image)
        cv.imwrite(f'../TreeHacks/media/generated_markers/marker_{id}.png', marker_image)



def aug_image(frame, source, destination_points):
    
    source_height, source_width = source.shape[:2]
    frame_height, frame_width = frame.shape[:2]
    
    mask = np.zeros((frame_height, frame_width), dtype=np.uint8)
    
    # top left, right, bot left, right
    source_points = np.array([[0,0], [source_width, 0], [source_width, source_height], [0, source_width]])
    
    # homography
    H, _ = cv.findHomography(srcPoints=source_points, dstPoints = destination_points)
    
    # warp perspective
    
    warp_image = cv.warpPerspective(source, H, (frame_width, frame_height))
    #cv.imshow('warp image', warp_image)
    
    # fill the aruco with the image
    cv.fillConvexPoly(mask, destination_points, 255)
    res = cv.bitwise_and(warp_image, warp_image, frame, mask=mask)
    return res




# read/load images from directory
def load_images(dir):
    images = []
    files = os.listdir(dir)
    for f in files:
        image_path = os.path.join(dir, f)
        image = cv.imread(image_path)
        images.append(image)
        
    return images    



@gzip.gzip_page
def cam(request):
    global v
    try:
        #print(len(img_list))
        img_list = load_images('../TreeHacks/media/images')

        createmarkers(len(img_list))
        cam = VideoCamera()
        
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    
    v = False
    return render(request, 'cam.html')



class VideoCamera(object):
    
    def __init__(self):
        self.video = cv.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        global v
        img_list = load_images('../TreeHacks/media/images')

        image = self.frame
        _, jpeg = cv.imencode('.jpg', image)
        
        cap = self.video
        (self.grabbed, self.frame) = cap.read()
        
        ret, frame = cap.read()
        
        # grayscale the image
        grayscaled = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        
        # detect cornors from aruco
        marker_corners, markers_IDs, rejected_markers = marker_detector.detectMarkers(grayscaled)
        aged = None
        ran = False
        if marker_corners:
        
            for ids, corners in zip(markers_IDs, marker_corners):
                
                # bounding lines around detected aruco
                
                cv.polylines(
                    frame, [corners.astype(np.int32)], True, (255,0,255), 4, cv.LINE_AA
                )
                
                # get rid of 1 from [1, 4, 2]
                corners = corners.reshape(4,2)
                corners = corners.astype(int)
                
                # checks for out of bounds; need to fix for uuid
                if len(img_list) > 0:
                    #print(ids[0],len(img_list))
                    if (ids[0]) <= len(img_list):
                        if v == False:
                            v = (verification())
                            while True:
                                messagefrom = client.messages.list(from_='+18187978710', to='+18552248052')
                                if len(messagefrom) > 0:
                                    print(messagefrom[0].body)
                                    if messagefrom[0].body == 'Y':
                                        v = True
                                        break
                                    else:
                                        quit()
                        
                        # matches id with image name (temporary unless better method is found)
                        aged = aug_image(frame, img_list[ids[0]-1], corners)

                                
                        
                    else:
                        aged = aug_image(frame, img_list[0], corners)
                    
                
                '''
                top_right = corners[0].ravel()
                top_left = corners[1].ravel()
                bottom_right = corners[2].ravel()
                bottom_left = corners[3].ravel()
                
                cv.putText(
                    frame,
                    f'id: {ids[0]}',
                    top_right,
                    cv.FONT_HERSHEY_COMPLEX,
                    1.5,
                    (255,0,0),
                    2,
                    cv.LINE_AA 
                )
                '''
                #print(ids, " ", corners)
            _, jpeg = cv.imencode('.jpg', aged)
        #return jpeg.tobytes()
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
        
def addID(request):
    global v
    if request.method == "POST":
        ID = IDModel()
        ID.patient_name = request.POST.get('patient_name')
        if len(request.FILES) != 0:
            ID.image = request.FILES['image']
        
        ID.save()
        messages.success(request,'ID Added')
        v = False
        return redirect('/add-id/')
    return render(request, 'add.html')

def index(request):
    return render(request, 'index.html')