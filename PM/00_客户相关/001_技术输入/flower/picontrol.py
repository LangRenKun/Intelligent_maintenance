# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO     #GPIO函数库
import Adafruit_DHT         #空气温湿度函数库
from picamera import PiCamera
import time
import re
import os

GPIO.setmode(GPIO.BCM)  #设置编号方式
GPIO.setwarnings(False) #屏蔽警告

GPIO_HUMI   = 17
GPIO_TRIG   = 5  # ultrasonic send-pin
GPIO_ECHO   = 6  # ultrasonic receive-pin
GPIO_WATER  = 23
GPIO_LIGHT  = 18
GPIO_INDLT  = 24

GPIO.setup(GPIO_TRIG, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_WATER, GPIO.OUT)
GPIO.setup(GPIO_LIGHT, GPIO.OUT)
GPIO.setup(GPIO_INDLT, GPIO.OUT)

#空气温湿度传感器型号
Humsensor = Adafruit_DHT.DHT22

#蓄水池深度
POOL_DEPTH = 38
MAX_DEPTH = 25

#配置文件
FILE_CONFIGURE  = "./configure.txt"
EXPR_SN         = r"<sn>\s?:\s*(\w*)</sn>"
EXPR_NAME       = r"<name>\s?:\s*(\w*)</name>"
EXPR_MAX        = r"<maxhumidity> \s?:\s*(\w*)</maxhumidity>"
EXPR_MIN        = r"<minhumidity> \s?:\s*(\w*)</minhumidity>"
#获取device的name,sn,湿度控制值
def getconfigure(expr):
    f2 = open(FILE_CONFIGURE)
    lines = f2.readlines()
    str = ''
    for line in lines:
        searchStr = re.search(expr, line, re.M | re.I)
        if searchStr:
            str = searchStr.group(1)
            break
    f2.close()
    return str

#获取device的sn
def getname():
    return getconfigure(EXPR_NAME)

def getsn():
    return getconfigure(EXPR_SN)

def getmaxhumi():
    return eval(getconfigure(EXPR_MAX))

def getminhumi():
    return eval(getconfigure(EXPR_MIN))



#设置湿度控制值
def setconfigure(expr,new_str):
    f1 = open(FILE_CONFIGURE, 'r')
    lines = f1.readlines()
    f1.close()
    f2 = open(FILE_CONFIGURE, 'w')
    for line in lines:
        searchStr = re.search(expr, line, re.M | re.I)
        if searchStr:
            str = searchStr.group(1)
            f2.write(line.replace(str,new_str))
        else:
            f2.write(line)
    f2.close()

def setminhumi(new_value):
    return setconfigure(EXPR_MIN,str(new_value))

def setmaxhumi(new_value):
    return setconfigure(EXPR_MAX,str(new_value))

#获取空气温度
def getairtemp():
    humidity, temperature = Adafruit_DHT.read_retry(Humsensor, GPIO_HUMI)
    return round(temperature, 2)

#获取空气湿度
def getairhumi():
    humidity, temperature = Adafruit_DHT.read_retry(Humsensor, GPIO_HUMI)
    return round(humidity, 2)

#测量水位
def getwaterlevel():
    # send 10us的方波脉冲
    GPIO.output(GPIO_TRIG, True)
    time.sleep(0.00001)  # 1us
    GPIO.output(GPIO_TRIG, False)

    # start recording
    while GPIO.input(GPIO_ECHO) == 0:
        pass
    start = time.time()

    # end recording
    while GPIO.input(GPIO_ECHO) == 1:
        pass
    end = time.time()

    # compute distance cm
    distance = round((end - start) * 343 / 2 * 100, 2)
    level = POOL_DEPTH - distance
    return round(level,2)

#浇水控制
def setwater(status):
    if status == True:
        GPIO.output(GPIO_WATER, 0)  # 低电平开启
    else:
        GPIO.output(GPIO_WATER, 1)  # 高电平关闭

#灯光控制
def setlight(status):
    if status == True:
        GPIO.output(GPIO_LIGHT, 0)  # 低电平开启
    else:
        GPIO.output(GPIO_LIGHT, 1)  # 高电平关闭

#指示灯
def indicator_light():
    for i in range(1,3):
        GPIO.output(GPIO_INDLT, 1)
        time.sleep(0.167)
        GPIO.output(GPIO_INDLT, 0)
        time.sleep(0.167)


def takepicture():
    camera = PiCamera()
    camera.start_preview()
    sleep(8)
    camera.capture('image.jpg')
    camera.stop_preview()
    #print(os.path.split(os.path.realpath(__file__))[0] + '/image.jpg')
    return os.path.split(os.path.realpath(__file__))[0] + '/image.jpg'