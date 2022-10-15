# import the necessary packages
from pyzbar.pyzbar import decode
import argparse
import cv2
import requests

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
        image = cv2.imread(args.image)
        barcodes = decode(image)  # detect and decode barcodes
        if barcodes is not None:
            for barcode in barcodes:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(image, (x, y), (x + w, y + h),
                              (0, 0, 255), 2)  # bounding box
                barcodeData = barcode.data.decode("utf-8")  # convert to string
                barcodeType = barcode.type
                # barcode data and barcode type on string img
                text = "{} ({})".format(barcodeData, barcodeType)
                cv2.putText(image, text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                print("[INFO] Found {}:\n{}".format(barcodeType, barcodeData))
                sendToGCOM(barcodeData)
        else:
            print("[INFO] No QR Code found")

    # for camera scanned images
    elif args.camera:

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
            image = decode(gray)

            for barcode in image:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(im, (x, y), (x + w, y + h),
                              (0, 0, 255), 2)  # bounding box
                barcodeData = barcode.data.decode("utf-8")  # convert to string
                barcodeType = barcode.type
                if barcodeData != barcodeDataLast:
                    print("[INFO] Found {}:\n{}".format(
                        barcodeType, barcodeData))
                    sendToGCOM(barcodeData)
                barcodeDataLast = barcodeData

            # Display image
            cv2.imshow("Camera Scan Index {}".format(args.camera), im)
            
             # Check if window was closed
            if cv2.waitKey(1) and cv2.getWindowProperty("Camera Scan Index {}".format(args.camera), cv2.WND_PROP_VISIBLE) != 1:
                break
        cv2.destroyAllWindows()

def sendToGCOM(data):
    try:
        acomPOST = requests.post(
            args.address, json={"data": data})
        print(acomPOST.text)
        return
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    main()
