#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep
from datetime import datetime

camera = PiCamera()
camera.resolution = (2592, 1944)
camera.framerate = 15



def main():
    camera.annotate_text = f"{datetime.now()}"
    camera.capture('/home/ekirill/camera.jpg')


if __name__ == "__main__":
    main()
