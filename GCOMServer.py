from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect, send
from threading import Lock

# Setup for Flask Server and Socket IO Websocket
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_ = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# Initialize Variables to store response
questionResponse = []
dateResponse = "No date scanned"
timeResponse = "No time scanned"
deviceResponse = "No device scanned"
sensorResponse = "No sensor scanned"
coordLatResponse = "No coord scanned"
coordLonResponse = "No coord scanned"

# Dummy coordinates
currentLon = -98.3
currentLat = 49.5

## -- SkyScanner POST Request Listener --
@socket_.on('camera_data_request', namespace= '/gcom')
def camera_data_request(message):
    # Check if coordinates are not blank, and if coordinates are close to current drone position
    if (message['lat'] != "No coord scanned" and message['lon'] != "No coord scanned"):
        distanceFromCoordinate = ((((message['lat'] - currentLat )**2) + ((message['lon'] - currentLon)**2) )**0.5)
        print("Distance is: " + str(distanceFromCoordinate))
        if (distanceFromCoordinate < 10):
            global coordLonResponse
            coordLonResponse = message['lon']
            global coordLatResponse
            coordLatResponse = message['lat']
            print("Coordinates are correct, skyscanner can shut down!")
            emit('camera_data_response', {'data': 200})
        else:
            emit('camera_data_response', {'data': 401})
    else: 
        print("Incorrect Data!")
        emit('camera_data_response', {'data': 401})

## --- Main Function ---

# Start the Websocket Server
if __name__ == '__main__':
    socket_.run(app, debug=True, port=3002)

