# Smart-Library

## Running

* Start the server:
```
python3 run.py
```
* Run the kivy app:
```
cd kivy
python3 lib_app.py
```

### Installing libraries(Linux)

1. Requires Python 3.x
2. ```sudo apt-get install libzbar0```
3. Install and upgrade pip, setuptools and virtualenv
```
python3 -m pip install --upgrade --user pip setuptools virtualenv
```
4. Load the virtualenv.
```
python3 -m virtualenv venv
source venv/bin/activate
```
5. Install kivy and kivy examples
```
python3 -m pip install kivy
python3 -m pip install kivy_examples
```
6. Install Flask and other dependencies.
```
python3 -m pip install flask
python3 -m pip install Flask-SQLAlchemy
python3 -m pip install pyjwt
python3 -m pip install pillow
python3 -m pip install pyzbar
python3 -m pip install pyzbar[scripts]
```
### Future goals
1. Building app.
2. Adding admin authorization.
3. Interfacing the hardware circuit.

