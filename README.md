# Skyscanner
`Skyscanner` is a QR code image reader for UAS competition

- Live feed QR code scanning using webcam FPV camera system
- Sample images QR code scanning
- Supports multiple QR code scanning

## Required Packages
- opencv
- pyzbar :: install from https://pypi.org/project/pyzbar/

## Usage
General usage is as follows:
- To scan sample images in /samples or other path:
```
python src/qr_code.py -i <img path>
```
- To scan live feed using a camera system:
```
python src/qr_code.py -c <device index>
```
**Device Index**

The device index indicates the order in which a device is plugged in
- webcam - 0
- fpv camera system - usually 1 or 2
