# -*- coding:utf-8 -*-



import time
import random

import paho.mqtt.client as mqtt

HOST = "192.168.31.82"
PORT = 1883
CLIENT = mqtt.Client()
CLIENT.username_pw_set("admin", "fnst1234!")

if __name__ == "__main__":
    """"""

    while 1:
        CLIENT.connect(HOST, PORT, 120)
        data_json = {
            'id': 'SW0021',
            'pid': 'W0003',
        }
        #CLIENT.publish('C0001/{0}/{1}'.format(data_json['pid'], data_json['id']), str(data_json), 1)
        CLIENT.publish('C0001/xxx', 'asdf', 1)
        print 'send'
        CLIENT.disconnect()
        time.sleep(3)

