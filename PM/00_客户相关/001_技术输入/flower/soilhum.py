# encoding: utf-8
#土壤湿度传感器
import smbus

#AD模块地址
__SOIL_ADDR = 0x48
__SOIL_BASE = 0X40
__SOIL_A0   = __SOIL_BASE + 0

#湿度标定
__AIR_HUM   = 255
__WATER_HUM = 115

def getsoilhum():
    bus = smbus.SMBus(1)
    bus.write_byte(__SOIL_ADDR, __SOIL_A0)
    value = bus.read_byte(__SOIL_ADDR)
    humidity = (__AIR_HUM - value) * 100 / (__AIR_HUM - __WATER_HUM)
    return round(humidity, 2)

