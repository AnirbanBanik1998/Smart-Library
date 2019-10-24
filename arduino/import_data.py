import serial
import time
import requests

try:
    arduino=serial.Serial('COM3', 9600)
except:
    arduino = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)
while 1:
    msg = arduino.readline()
    #print(msg.decode('utf-8'))
    string = msg.decode('utf-8')
    extract = string.split("\n")[0].strip()
    print(extract)
    data = {'rfid_id': extract}
    response = requests.put('http://127.0.0.1:5000/entry_exit', json=data)
    if response.status_code == 200:
        print(response.json())

    
    
