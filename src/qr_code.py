# import the necessary packages
from pyzbar.pyzbar import decode
import argparse
import cv2
import requests
import json

# initialize parser and parse arguments
ap = argparse.ArgumentParser(
    prog="skyscanner", description="scan QR codes from samples or camera")

ap.add_argument("-i", "--image", action="store",
                help="scan sample images using path to input image")
ap.add_argument("-c", "--camera", action="store",
                help="scan live feed using camera device index")
ap.add_argument("-a", "--address", action="store", help="Return address for QR Code data")

args = ap.parse_args()


def main():
    # for loaded sample input images
    if args.image:
        scanImage()
    # for camera scanned images
    elif args.camera:
        runCameraScanner()

def scanImage():
    image = cv2.imread(args.image)
    barcodeDataset = decodeInput(image)
    if len(barcodeDataset) > 0:
        for barcodeData in barcodeDataset:
            sendToGCOM(barcodeData, True)
    else:
        sendToGCOM(barcodeDataset, False)

def runCameraScanner():
    barcodeDataLast = None
    # open cv video camera capture
    window = cv2.namedWindow("Camera Scan Index {}".format(args.camera))
    cap = cv2.VideoCapture(int(args.camera))

    while True:
        ret, im = cap.read()
        if not ret:
            continue

        # Read Image
        size = im.shape
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY, dstCn=0)

        barcodeDataset = decodeInput(im)
        for barcodeData in barcodeDataset:
            sendToGCOM(barcodeData, True)

        # Display image
        cv2.imshow("Camera Scan Index {}".format(args.camera), im)
        
            # Check if window was closed
        if cv2.waitKey(1) and cv2.getWindowProperty("Camera Scan Index {}".format(args.camera), cv2.WND_PROP_VISIBLE) != 1:
            break
    cv2.destroyAllWindows()

def decodeInput(image):
    barcodeData = []
    barcodes = decode(image)
    for barcode in barcodes:
        barcodeData.append(barcode.data.decode("utf-8"))  # convert to string
    return barcodeData

def sendToGCOM(data, found):
    jsonData = json.dumps({"found": found, "data": data})
    try:
        acomPOST = requests.post(
            args.address, json=jsonData)
        print(acomPOST.text)
        return
    except Exception as e:
        print(e)
    print(jsonData)

if __name__ == '__main__':
    main()
