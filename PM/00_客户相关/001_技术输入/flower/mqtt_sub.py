# -*- coding:utf-8 -*-
import json
import time
import random
from datetime import datetime

import paho.mqtt.client as mqtt

HOST = "192.168.31.82"
PORT = 1883
CLIENT = mqtt.Client()
CLIENT.username_pw_set("admin", "fnst1234!")
INDEX =1
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc), userdata)
    client.subscribe("C0001/#", 1)    # 订阅top


def on_message(client, userdata, msg):
    if msg:
        global INDEX
        print INDEX
        INDEX =INDEX+1

        print msg.payload
    else:
        print("数据为空")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


if __name__ == "__main__":
    """mqtt_test"""

    CLIENT.on_connect = on_connect
    CLIENT.on_message = on_message
    CLIENT.on_disconnect = on_disconnect
    try:
        CLIENT.connect(HOST, PORT, 120)
        CLIENT.loop_forever()
    except KeyboardInterrupt:
        print("Interrupt received")
        CLIENT.disconnect()
    except Exception as error:
        print("error: ", error)
        CLIENT.disconnect()