# import the necessary packages
from pyzbar import pyzbar
import zbar
import argparse
import cv2
from PIL import Image,ImageColor
import numpy as np
import wx 

# initialize parser and parse arguments
ap = argparse.ArgumentParser(prog="skyscanner",
	description="scan QR codes from samples or camera")

ap.add_argument("-i", "--image", action="store",
	help="scan sample images using path to input image")
ap.add_argument("-c", "--camera", action="store",
	help="scan live feed using camera device index")
args = ap.parse_args()

def main():
	# for loaded sample input images
	if args.image:
		image = cv2.imread(args.image)
		barcodes = pyzbar.decode(image)		#detect and decode barcodes

		for barcode in barcodes:
			(x, y, w, h) = barcode.rect
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)	# bounding box
		
			barcodeData = barcode.data.decode("utf-8")	# convert to string
			barcodeType = barcode.type
		
			text = "{} ({})".format(barcodeData, barcodeType)	# barcode data and barcode type on string img
			cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
				0.5, (0, 0, 255), 2)
		
			print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

		cv2.imshow("Image", image)
		cv2.waitKey(0)

	# for camera scanned images
	elif args.camera:

		# Display data in new window
		app = wx.App(False)
		frame = TextData(None)

		cap = cv2.VideoCapture(int(args.camera))	#open cv video camera capture

		scanner = zbar.ImageScanner()
		scanner.parse_config('enable')

		while True:
			ret, im = cap.read()
			if not ret:
				continue 
			
			# Read Image
			size = im.shape
			gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY, dstCn=0)
			pil = Image.fromarray(gray)
			width, height = pil.size
			raw = pil.tobytes()
			image = zbar.Image(width, height, 'Y800', raw)
			scanner.scan(image)

			for symbol in image:
				print ("DECODED: {}, DATA: {}".format(symbol.type, symbol.data))
				topLeftCorners, bottomLeftCorners, bottomRightCorners, topRightCorners = [item for item in symbol.location]

				#2D image points	
				image_points = np.array([
									(int((topLeftCorners[0]+topRightCorners[0])/2), int((topLeftCorners[1]+bottomLeftCorners[1])/2)),     # Nose
									topLeftCorners,
									topRightCorners,
									bottomLeftCorners,
									bottomRightCorners      # Right mouth corner
								], dtype="double")
				
				# 3D model points
				model_points = np.array([
									(0.0, 0.0, 0.0),             # Center
									(-225.0, 170.0, -135.0),     # Top Left
									(225.0, 170.0, -135.0),      # Top Right
									(-150.0, -150.0, -125.0),    # Bottom Left
									(150.0, -150.0, -125.0)      # Bottom Right
									])

				# Camera internals
				focal_length = size[1]
				center = (size[1]/2, size[0]/2)
				camera_matrix = np.array(
								[[focal_length, 0, center[0]],
								[0, focal_length, center[1]],
								[0, 0, 1]], dtype = "double"
								)
				
				print ("Camera Matrix :\n {}".format(camera_matrix))
				
				dist_coeffs = np.zeros((4,1)) # no lens distortion
				(success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
				
				print ("Rotation Vector:\n {}".format(rotation_vector))
				print ("Translation Vector:\n {}".format(translation_vector))
				
				# Project 3D point (0, 0, 1000.0) onto the image plane with line out of the nose
				(nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 100.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)
				
				for p in image_points:
					cv2.circle(im, (int(p[0]), int(p[1])), 3, (0,0,255), -1)
				
				p1 = ( int(image_points[0][0]), int(image_points[0][1]))
				p2 = ( int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
				
				# frame
				cv2.line(im, topLeftCorners, topRightCorners, (255,0,0),2)
				cv2.line(im, topLeftCorners, bottomLeftCorners, (255,0,0),2)
				cv2.line(im, topRightCorners, bottomRightCorners, (255,0,0),2)
				cv2.line(im, bottomLeftCorners, bottomRightCorners, (255,0,0),2)

				# diagonal
				cv2.line(im, bottomLeftCorners, p2, (255,0,0), 2)
				cv2.line(im, topLeftCorners, p2, (255,0,0), 2)
				cv2.line(im, bottomRightCorners, p2, (255,0,0), 2)
				cv2.line(im, topRightCorners, p2, (255,0,0), 2)

				# text data
				text = "{} ({})".format(symbol.data, symbol.type)
				cv2.putText(im, text, (topLeftCorners[0], topLeftCorners[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
					0.5, (0, 0, 255), 2)

				# display data in new window
				frame.write_data(text)

			# Display image
			cv2.imshow("Camera Scan Index {}".format(args.camera), im)
			frame.Show()

			# Wait for the exit key
			cv2.waitKey(1)

		cv2.waitKey(0)

    	app.MainLoop() 

class TextData(wx.Frame):

	data_list = []

	def __init__(self, *args, **kwargs):
		super(TextData, self).__init__(*args, **kwargs)

		panel = wx.Panel(self)
		
		self.SetSize((600,400))
		self.SetTitle("QR Code Text Data")
		self.Centre()
		self.new_data = wx.TextCtrl(self, id = -1, pos = wx.DefaultPosition,
			size = (600,400), style = wx.TE_MULTILINE | wx.TE_READONLY)

	def write_data(self, decoded):
		if decoded not in set(TextData.data_list):
			self.new_data.AppendText(decoded + "\n\n")
			TextData.data_list.append(decoded)


if __name__ == '__main__': 
	main() 