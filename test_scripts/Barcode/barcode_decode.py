import sys
from pyzbar.pyzbar import decode
from PIL import Image

img_path = sys.argv[1]  # Image Path as a command-line argument
img = Image.open(img_path)
supported_types = ['EAN8', 'EAN13', 'CODE39', 'CODE128']

def decode_bar(img):
    barcode = decode(img)[0]
    if barcode.type in supported_types:
        return barcode.data.decode('utf-8')

    return None

print(decode_bar(img))

