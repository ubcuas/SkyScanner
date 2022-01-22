from os import times
from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect, send
from threading import Lock
from pyzbar.pyzbar import decode
import argparse
import cv2

from socketIO_client import SocketIO, BaseNamespace

import sys
# adding models to the system path
sys.path.insert(0, '../models')
from scannerClient import scannerClient

# Initialize Variables
questionResponse = []
dateResponse = "No date scanned"
timeResponse = "No time scanned"
deviceResponse = "No device scanned"
sensorResponse = "No sensor scanned"
coordLatResponse = "No coord scanned"
coordLonResponse = "No coord scanned"

# ---- Helper Functions ----

# Helper function to read barcode data
def run_camera(responseData):
    barcodeDataLast = None
    cap = cv2.VideoCapture(int(0))
    status = True

    while status:
        ret, im = cap.read()
        if not ret:
            continue
        
        # Read Image
        size = im.shape
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY, dstCn=0)
        image = decode(gray)

        for barcode in image:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)	# bounding box
            barcodeData = barcode.data.decode("utf-8")	# convert to string
            barcodeType = barcode.type
            if barcodeData != barcodeDataLast:
                # JSON Stuff is printed here
                # Need to make new function that makes a post command to GCOM instead of print
                print ("[INFO] Found {}:\n{}".format(barcodeType, barcodeData))
                splitQuestions = barcodeData.split('\n')
                if (len(splitQuestions) > 1):
                    questionsList = splitQuestions[1].split('?')
                    for q in questionsList:
                        if (q != ''):
                            questions = []
                            questions.append(q.strip())
                    responseData.questionResponse = questions
                    dataList = splitQuestions[2].split(';')
                    responseData.dateResponse = dataList[0].strip()
                    responseData.timeResponse = dataList[1].strip()
                    responseData.deviceResponse = dataList[2].strip()
                    responseData.sensorResponse = dataList[3].strip()
                    coord = dataList[4].strip().split(',')
                    responseData.coordLatResponse = coord[0].strip()
                    responseData.coordLonResponse = coord[1].strip()
                barcodeDataLast = barcodeData

        # Display image
        cv2.imshow("Camera Scan Index {}".format(0), im)

        if barcodeDataLast != None:
            if (responseData.coordLatResponse != "No coord scanned"):
                cv2.destroyAllWindows()
                cv2.waitKey(1)
                cap.release()
                status = False

# Helper function that checks response from GCOM. If coordinates look correct, save scanned data to text file
## Note: For now, this text file is hardcoded as "USC_Data.txt"
def checkStatus(*randomString):
    global responseData
    if (randomString[0]['data'] == 200):
        print('Status: ',randomString[0]['data'])
        fileName = 'USC_Data.txt'
        file = open(fileName, 'w')
        count = 1
        for q in responseData.questionResponse:
            file.write("Question #" + str(count) + " : " + q + "?" + "\n")
            count = count + 1
        file.write("Date: " + responseData.dateResponse + "\n")
        file.write("Time: " + responseData.timeResponse + "\n")
        file.write("Device: " + responseData.deviceResponse + "\n")
        file.write("Sensor: " + responseData.sensorResponse + "\n")
        file.write("Coordinates: " + responseData.coordLatResponse + ", " + responseData.coordLonResponse)
        file.close()
        print("Saved data to: " + fileName)
    else: 
        print("There has been a mistake! Please rescan the QR code")
        run_camera(responseData)
        chat.emit('camera_data_request', {'lat': float(responseData.coordLatResponse), 'lon': float(responseData.coordLonResponse)})
        socket.wait(seconds = 1)

# --- Main Function --- 

responseData = scannerClient()

# Call camera
print("The camera is active, please scan the QR Code!")
run_camera(responseData)

# Start socket connection 
print("Starting socket")
socket = SocketIO('localhost', 3002)
print("Opening NameSpace")
chat = socket.define(BaseNamespace, '/gcom')

# Listen to response from GCOM Server
chat.on('camera_data_response', checkStatus)

# Send a request to GCOM 
print("Sending data to GCOM...")
chat.emit('camera_data_request', {'lat': float(responseData.coordLatResponse), 'lon': float(responseData.coordLonResponse)})
socket.wait(seconds = 1)
