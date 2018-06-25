# -*- coding:utf-8 -*-
from picamera import PiCamera
from time import sleep
import os

camera = PiCamera()
camera.start_preview()
sleep(8)
camera.capture('image.jpg')
camera.stop_preview()
print(os.path.split(os.path.realpath(__file__))[0]+'/image.jpg')