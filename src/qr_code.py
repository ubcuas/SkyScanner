# import the necessary packages
from pyzbar.pyzbar import decode
import argparse
import cv2
import requests

# initialize parser and parse arguments
ap = argparse.ArgumentParser(prog="skyscanner", description="scan QR codes from samples or camera")

ap.add_argument("-i", "--image", action="store", help="scan sample images using path to input image")
ap.add_argument("-c", "--camera", action="store", help="scan live feed using camera device index")
args = ap.parse_args()

def main():
    # for loaded sample input images
    if args.image:
        image = cv2.imread(args.image)
        barcodes = decode(image)  # detect and decode barcodes
        if barcodes is not None:
            for barcode in barcodes:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # bounding box
                barcodeData = barcode.data.decode("utf-8")  # convert to string
                barcodeType = barcode.type
                # barcode data and barcode type on string img
                text = "{} ({})".format(barcodeData, barcodeType)
                cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                print("[INFO] Found {}:\n{}".format(barcodeType, barcodeData))
        cv2.imshow("Image", image)
        cv2.waitKey(0)

    # for camera scanned images
    elif args.camera:

        barcodeDataLast = None
        # open cv video camera capture
        cap = cv2.VideoCapture(int(args.camera))

        while True:
            ret, im = cap.read()
            if not ret:
                continue

            # Read Image
            size = im.shape
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY, dstCn=0)
            image = decode(gray)

            for barcode in image:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)  # bounding box
                barcodeData = barcode.data.decode("utf-8")  # convert to string
                barcodeType = barcode.type
                if barcodeData != barcodeDataLast:
                    print("[INFO] Found {}:\n{}".format(barcodeType, barcodeData))

                    try:
                        output = list(map((lambda x: x.strip()), barcodeData.split(";")[-1].split(", ")))
                        generatedMission = {
                            'wps': [
                                {
                                    'lat': float(output[0]),
                                    'lon': float(output[1]),
                                }
                            ],
                            'takeoffAlt': 60,
							'rtl': False,
                        }
                        acomPOST = requests.post(
                            'http://51.222.12.76:5000/aircraft/mission', json=generatedMission)
                        print(acomPOST.text)

                    except Exception as e:
                        print(e)

                barcodeDataLast = barcodeData

            # Display image
            cv2.imshow("Camera Scan Index {}".format(args.camera), im)

            # Wait for the exit key
            cv2.waitKey(1)

        cv2.waitKey(0)


if __name__ == '__main__':
    main()
