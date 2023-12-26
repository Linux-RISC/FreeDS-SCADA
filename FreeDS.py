#!/usr/bin/env python3

# https://www.emqx.com/en/blog/how-to-use-mqtt-in-python
# https://pypi.org/project/paho-mqtt/
# python3.6

import random
import time

from paho.mqtt import client as mqtt_client
from datetime import datetime

broker_name = '192.168.9.204'
broker_port = 1883

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = ''
password = ''

FDS_name = 'freeds_57D0'
topic_FDS_stat_pwm = FDS_name+"/stat/pwm"
topic_FDS_tempTermo = FDS_name+"/tempTermo"
topic_FDS_b_LowTempManualMode = FDS_name+"/FDS_b_LowTempManualMode"
topic_FDS_LowTempManualMode = FDS_name+"/FDS_LowTempManualMode"
topic_FDS_TempIncreaseAutoMode = FDS_name+"/FDS_TempIncreaseAutoMode"
topic_send = FDS_name+"/cmnd"

FDS_stat_pwm = "AUTO"
FDS_tempTermo = 0
FDS_b_LowTempManualMode = False
FDS_LowTempManualMode = 0
FDS_TempIncreaseAutoMode = 0

bReconnection = False

#----------------------------------------------------------------------
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        # dd/mm/YY H:M:S
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string)
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n" % rc)

        if bReconnection == True:
           subscribe(client)
           print ("Client resubscribed\n")

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker_name, broker_port)
    return client
#----------------------------------------------------------------------
#FIRST_RECONNECT_DELAY = 1
#RECONNECT_RATE = 2
#MAX_RECONNECT_COUNT = 12
#MAX_RECONNECT_DELAY = 60

def on_disconnect(client, userdata, rc):
    global bReconnection
    bReconnection = True

    # dd/mm/YY H:M:S
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string)
    #logging.info("Disconnected with result code: %s", rc)
    print("Disconnected with result code: %s" % rc)
    print("")

    #reconnect_count, reconnect_delay = 1, FIRST_RECONNECT_DELAY
    reconnect_delay = 10
    #while reconnect_count < MAX_RECONNECT_COUNT:
    while True:
        # dd/mm/YY H:M:S
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string)
        #logging.info("Reconnecting in %d seconds...", reconnect_delay)
        print("Reconnecting in %d seconds..." % reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            #logging.info("Reconnected successfully!")
            print("Reconnected successfully!\n")
            return
        except Exception as err:
            #logging.error("%s. Reconnect failed. Retrying...", err)
            print("%s. Reconnection failed. Retrying...\n" % err)

        #reconnect_delay *= RECONNECT_RATE
        #reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        #reconnect_count += 1
    #logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
#----------------------------------------------------------------------
def publish(client, msg):
        time.sleep(1)
        result = client.publish(topic_send, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic_send}`")
        else:
            print(f"Failed to send message to topic {topic}")
#----------------------------------------------------------------------
def setManualMode(client):
        msg = '{"command":"pwmman","payload":"1"}'
        publish(client,msg)
#----------------------------------------------------------------------
def setAutomaticMode(client):
        msg = '{"command":"pwmman","payload":"0"}'
        publish(client,msg)
#----------------------------------------------------------------------
def setFanOn(client):
        msg = '{"command":"relay4","payload":"1"}'
        publish(client,msg)
#----------------------------------------------------------------------
def setFanOff(client):
        msg = '{"command":"relay4","payload":"0"}'
        publish(client,msg)
#----------------------------------------------------------------------
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global FDS_stat_pwm
        global FDS_tempTermo
        global FDS_b_LowTempManualMode
        global FDS_LowTempManualMode
        global FDS_TempIncreaseAutoMode

        # dd/mm/YY H:M:S
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string)
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        topic = msg.topic

        if topic == topic_FDS_tempTermo:
           FDS_tempTermo = float(msg.payload.decode())
        elif topic == topic_FDS_stat_pwm:
           FDS_stat_pwm = msg.payload.decode()
        elif topic == topic_FDS_b_LowTempManualMode:
           FDS_b_LowTempManualMode = True if msg.payload.decode()=='true' else False
        elif topic == topic_FDS_LowTempManualMode:
           FDS_LowTempManualMode = float(msg.payload.decode())
        elif topic == topic_FDS_TempIncreaseAutoMode:
           FDS_TempIncreaseAutoMode = float(msg.payload.decode())
        else:
           return

        print ("FDS_stat_pwm="+FDS_stat_pwm);
        print ("FDS_tempTermo="+str(FDS_tempTermo));
        print ("FDS_b_LowTempManualMode="+str(FDS_b_LowTempManualMode));
        print ("FDS_LowTempManualMode="+str(FDS_LowTempManualMode));
        print ("FDS_TempIncreaseAutoMode="+str(FDS_TempIncreaseAutoMode));
 
        # 1. FDS_b_LowTempManualMode has to be True
        if not FDS_b_LowTempManualMode:
           print ("")
           return 

        # if AUTO mode and temperature<=FDS_LowTempManualMode, switch to manual mode
        if FDS_stat_pwm=="AUTO" and FDS_tempTermo <= FDS_LowTempManualMode:
            print("Switching to manual mode")
            print("Switching the fan on")
            setManualMode(client)  
            # enter on console: relay4AsFanSwitch 1
            setFanOn(client)  

        # if MAN mode and temperature>=FDS_LowTempManualMode+FDS_TempIncreaseAutoMode, return to automatic mode
        if FDS_stat_pwm=="MAN" and FDS_tempTermo >= (FDS_LowTempManualMode+FDS_TempIncreaseAutoMode):
            print("Returning to automatic mode")
            #print("Switching the fan off")
            setAutomaticMode(client)  
            #setFanOff(client)  

        print ("")
    		
    client.subscribe(topic_FDS_stat_pwm)
    client.subscribe(topic_FDS_tempTermo)
    client.subscribe(topic_FDS_b_LowTempManualMode)
    client.subscribe(topic_FDS_LowTempManualMode)
    client.subscribe(topic_FDS_TempIncreaseAutoMode)
    client.on_message = on_message       	
#----------------------------------------------------------------------
def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()
#----------------------------------------------------------------------
if __name__ == '__main__':
    run()
