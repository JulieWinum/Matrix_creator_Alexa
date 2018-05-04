#! /usr/bin/env python

import os
import random
import time
import random
from creds import *
import requests
import json
import time
import re
import subprocess
import alsaaudio, time, audioop
from memcache import Client

import zmq
import time
from matrix_io.proto.malos.v1 import driver_pb2
from matrix_io.proto.malos.v1 import io_pb2

# Setup
creator_ip = os.environ.get('CREATOR_IP', '127.0.0.1')

creator_everloop_base_port = 20013 + 8

context = zmq.Context()
config_socket = context.socket(zmq.PUSH)
config_socket.connect('tcp://{0}:{1}'.format(creator_ip, creator_everloop_base_port))

recorded = False
servers = ["127.0.0.1:11211"]
mc = Client(servers, debug=1)
path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))

def setEverloopColor(red=0, green=0, blue=0, white=0):
    config = driver_pb2.DriverConfig()
    image = []
    for led in range (35):
        ledValue = io_pb2.LedValue()
        ledValue.blue = blue
        ledValue.red = red
        ledValue.green = green
        ledValue.white = white
        image.append(ledValue)

    config.image.led.extend(image)
    config_socket.send(config.SerializeToString())


def internet_on():
    print "Checking Internet Connection"
    try:
        r = requests.get('https://api.amazon.com/auth/o2/token')
        print "Connection OK"
        return True
    except:
        print "Connection Failed"
        return False


def gettoken():
    token = mc.get("access_token")
    refresh = refresh_token
    if token:
        return token
    elif refresh:
        payload = {"client_id": Client_ID, "client_secret": Client_Secret,
                   "refresh_token": refresh, "grant_type": "refresh_token", }
        url = "https://api.amazon.com/auth/o2/token"
        print("payload=")
        print(payload)
        r = requests.post(url, data=payload)
        print("res=")
        print(r.text)
        resp = json.loads(r.text)
        mc.set("access_token", resp['access_token'], 3570)
        return resp['access_token']
    else:
        return False


def alexa():
    url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
    headers = {'Authorization': 'Bearer %s' % gettoken()}
    d = {  # a dict
        "messageHeader": {
            "deviceContext": [
                {
                    "name": "playbackState",
                    "namespace": "AudioPlayer",
                    "payload": {
                            "streamId": "",
                            "offsetInMilliseconds": "0",
                            "playerActivity": "IDLE"
                    }
                }
            ]
        },
        "messageBody": {
            "profile": "alexa-close-talk",
            "locale": "en-us",
            "format": "audio/L16; rate=16000; channels=1"
        }
    }
    with open(path + 'recording.raw') as inf:
        files = [  # a list
            ('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
            ('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
        ]
        print type(files)
        print type(d)
        r = requests.post(url, headers=headers, files=files)
    if r.status_code == 200:
        for v in r.headers['content-type'].split(";"):
            if re.match('.*boundary.*', v):
                boundary = v.split("=")[1]
        data = r.content.split(boundary)
        for d in data:
            if (len(d) >= 1024):
                audio = d.split('\r\n\r\n')[1].rstrip('--')
                print type(audio)
        with open(path + "response.mp3", 'wb') as f:
            f.write(audio)
        os.system(
            'mpg123 -q {}1sec.mp3 {}response.mp3'.format(path + "/assets/", path))
    else:
        print "requests returned r.status_code = %r" % r.status_code


def start():
   setEverloopColor(0,0,0,10)
   cmd = "./wakeword/wake_word"

   subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
   time.sleep(1)

   fifo = open("/tmp/wakeword_pipe")

   while True:
     if "alexa" in fifo.readline():
       print "ALEXA!!!!"

       setEverloopColor(10,0,0,0)
       os.system('mpg123 -q {}start.mp3'.format(path))

       capture_audio()

       os.system('mpg123 -q {}stop.mp3'.format(path))
       setEverloopColor(0,0,10,0)
       alexa()

       setEverloopColor(0,0,0,10)


def capture_audio():
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL)

    inp.setchannels(1) #son mono
    inp.setrate(16000) #freq d'échantillonage
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(512)

    loops=290
    silence_counter = 80
    silence_thershold = 2500
    rf = open(path + 'recording.raw', 'w')
    while loops > 0:
      loops -= 1
      l, data = inp.read()
      print audioop.max(data,2)
      if audioop.max(data,2) < silence_thershold:
        silence_counter -= 1
        if silence_counter == 0:
          print "Silence detected "
          break
      else:
        silence_counter=60
      if l:
        rf.write(data)

    rf.close()


if __name__ == "__main__":
    print "This is a MATRIX Creator demo - not ready for production"

    while internet_on() == False:
        print "."
    token = gettoken()
    os.system('mpg123 -q {}1sec.mp3 {}hello.mp3'.format(path +
                                                        "/assets/", path + "/assets/"))
    while True:
        start()
