# -*- coding:utf-8 -*-
import time
import paho.mqtt.client as mqtt
import threading
import re                   #配置文件
import picontrol            #引入GPIO控制函数库
import soilhum              #引入土壤湿度函数库
import illumi               #引入光照强度函数库
import sys

class Access:
    def __init__(self,name):
        self.name = name
    def read(self):
        pass
    def write(self):
        pass

class Humidity(Access):
    def __init__(self):
        self.name = "Humidity"
        self.temp=25
        self.humidity=60
    def read(self):
        self.temp = picontrol.getairtemp()
        self.humidity = picontrol.getairhumi()
        return [self.temp,self.humidity]
class SoilHumidity(Access):
    def __init__(self):
        self.name = "SoilHumidity"
        self.humidity=80
    def read(self):
        self.humidity = soilhum.getsoilhum()
        return self.humidity
class Illumi(Access):
    def __init__(self):
        self.name = "Illumi"
        self.intensity=150
    def read(self):
        self.intensity = illumi.getIlluminance()
        return self.intensity
class WaterLevel(Access):
    def __init__(self):
        self.name = "WaterLevel"
        self.level = 15
    def read(self):
        self.level = picontrol.getwaterlevel()
        return self.level

class Watering(Access):
    def __init__(self):
        self.name = "Watering"
        picontrol.setwater(False)
        self.status = False
    def read(self):
        return self.status
    def write(self,status):
        picontrol.setwater(status)
        self.status = status

class Light(Access):
    def __init__(self):
        self.name = "Light"
        picontrol.setlight(False)
        self.status = False
    def read(self):
        return self.status
    def write(self,status):
        picontrol.setlight(status)
        self.status = status


class Device:
    def __init__(self):
        self.access_list={"Humidity": Humidity(),"SoilHumidity":SoilHumidity(),"Illumi":Illumi(),"WaterLevel":WaterLevel(),"Watering":Watering(),"Light":Light()}
        self.name=self.get_name()
        self.sn=self.get_sn()
        self.maxhumi = self.get_maxhumi()
        self.minhumi = self.get_minhumi()
        self.auto = True
    def get_name(self):
        return picontrol.getname()
    def get_sn(self):
        return picontrol.getsn()
    def get_maxhumi(self):
        return picontrol.getmaxhumi()
    def get_minhumi(self):
        return picontrol.getminhumi()


class DeviceApi:
    def __init__(self,device):
        self.device = device


    def mqtt_send(self,topic,payload):
        mqtt_api = Mqtt(self)
        mqtt_api.send(topic,payload)
    def send_heart(self):
        topic = "FlowerBuddy/JNH/DEV/"+self.device.sn+"/DeviceInfo"
        msg =self.device.get_name()+";"
        humidity=self.device.access_list["Humidity"].read()
        msg += str(humidity[0])+";"+str(humidity[1])+";"
        msg += str(self.device.access_list["SoilHumidity"].read()) + ";"
        msg += str(self.device.access_list["Illumi"].read()) + ";"
        msg += str(self.device.access_list["WaterLevel"].read()) + ";"
        msg += str(self.device.access_list["Watering"].read()) + ";"
        msg += str(self.device.access_list["Light"].read())+";"
        msg += str(self.device.auto) + ";"
        self.mqtt_send(topic,msg)

    def send_policy(self):
        topic = "FlowerBuddy/JNH/DEV/" + self.device.sn + "/Policy"
        msg = "soilhumData" + ":"
        msg += str(self.device.get_minhumi()) + "-"
        msg += str(self.device.get_maxhumi())
        self.mqtt_send(topic, msg)

    def set_policy(self,max,min):
        picontrol.setmaxhumi(max)
        picontrol.setminhumi(min)

    def action_wartering(self):
        if self.device.access_list["SoilHumidity"].read() < self.device.maxhumi:
            self.once_water()
        else:
            self.device.access_list["Watering"].write(False)
            #
            print ("过多的爱会变成溺爱哦！")
            self.send_heart()

    def action_light_on(self):
        self.device.access_list["Light"].write(True)
        time.sleep(0.1)
        self.send_heart()

    def action_light_off(self):
        self.device.access_list["Light"].write(False)
        time.sleep(0.1)
        self.send_heart()

    def action_auto_on(self):
        self.device.auto=True
        self.send_heart()

    def action_auto_off(self):
        self.device.auto=False
        self.send_heart()

    def auto_water(self):
        if self.device.auto:
            if self.device.access_list["SoilHumidity"].read() < self.device.minhumi:
                print("启动浇水！")
                time = 0
                while self.device.access_list["SoilHumidity"].read() < self.device.maxhumi:
                    self.once_water()
                    time = time + 1
                    if time == 5 : #最多5次防止传感器失灵
                        print('连续浇水5次湿度为达标，请检测土壤湿度传感器！')
                        break
                self.device.access_list["Watering"].write(False)
                #
                print("我已经喝饱了！")
                self.send_heart()
            else:
                print("我还不口渴！")

    def once_water(self):
        self.device.access_list["Watering"].write(True)
        time.sleep(0.8)
        self.send_heart()
        self.device.access_list["Watering"].write(False)
        time.sleep(1.0)


class Mqtt:
    def __init__(self,device_api):
        #self.user = "admin"
        #self.passwd = "fnst1234!"
        #self.host = "192.168.31.82"
        # self.port = 1883

        #云服务器测试
        self.user = "iceykjhp"
        self.passwd = "xDcTaQARqJaM"
        self.host = "m13.cloudmqtt.com"
        self.port = 13173

        self.device_api = device_api
    def send(self,topic,msg):
        CLIENT = mqtt.Client()
        CLIENT.username_pw_set(self.user, self.passwd)
        CLIENT.connect(self.host, self.port, 120)
        #CLIENT.connect("iot.eclipse.org", 1883, 60)
        CLIENT.publish(topic,msg,1)
        CLIENT.disconnect()
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print (cur_time+" MQTT:PUB "+topic+" "+msg)
    def sub(self):
        CLIENT = mqtt.Client(userdata=self.device_api)
        CLIENT.on_connect = on_connect
        CLIENT.on_message = on_message
        CLIENT.on_disconnect = on_disconnect
        try:

            CLIENT.username_pw_set(self.user, self.passwd)
            CLIENT.connect(self.host, self.port, 120)

            cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print (cur_time + " NOTICE start read msg")
            CLIENT.loop_forever()
            cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print (cur_time + " NOTICE end read msg")
        except KeyboardInterrupt:
            print("Interrupt received")
            CLIENT.disconnect()
        except Exception as error:
            print("error11: ", error+__file__+sys._getframe().f_lineno)
            CLIENT.disconnect()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc), userdata)
    device_api = userdata
    id = device_api.device.get_sn()
    client.subscribe("FlowerBuddy/JNH/RMT/"+id+"/#", 1)  # 订阅top

def on_message(client, userdata, msg):
    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    device_api = userdata
    if msg:
        topic = msg.topic
        payload = (msg.payload).decode()
        print (cur_time+" MQTT:GET "+topic+" "+payload)
        if topic.find("Action"):
            msgs = payload.split(";")
            for cur_msg in msgs:
                key_value = cur_msg.split(":")
                if key_value[0] == "light":
                    if key_value[1]=="on":
                        device_api.action_light_on()
                    elif key_value[1]=="off":
                        device_api.action_light_off()
                elif key_value[0] == "water":
                    if key_value[1] == "on":
                        device_api.action_wartering()
                elif key_value[0] == "auto":
                    if key_value[1] == "on":
                        device_api.action_auto_on()
                    elif key_value[1] == "off":
                        device_api.action_auto_off()
    else:
        print (cur_time + "   {NONE}")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        print ("disconnection")

if __name__ == "__main__":
    device = Device()
    device_api = DeviceApi(device)
    mqtt_api = Mqtt(device_api)
    #mqtt_api.sub()
    t = threading.Thread(target=mqtt_api.sub)
    t.start()
    while True:
        device_api.send_heart()
        device_api.auto_water()
        time.sleep(10)
