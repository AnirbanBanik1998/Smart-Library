from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout 
import time
import requests

from pyzbar.pyzbar import decode
from PIL import Image 
# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.

# Declare both screens
class MenuScreen(Screen):
    pass

class ScannerScreen(Screen):
    def capture(self):
        #Function to capture the images and give them the names
        #according to their captured time and date.
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        img_file = "IMG_{}.png".format(timestr)
        camera.export_to_png(img_file)
        print("Captured")
        barcode_id = self.decode(img_file)
        print(barcode_id)
    
    def decode(self, img_file):
        img = Image.open(img_file)
        supported_types = ['EAN8', 'EAN13', 'CODE39', 'CODE128']
        try:
            barcode = decode(img)[0]
            if barcode.type in supported_types:
                return barcode.data.decode('utf-8')
        except Exception as e:
            print(e)
        return None

    def issue(barcode_id):
        url = 'http://127.0.0.1/issue'


class TestApp(App):

    def build(self):
        return Builder.load_file("new_test.kv")

if __name__ == '__main__':
    TestApp().run()
