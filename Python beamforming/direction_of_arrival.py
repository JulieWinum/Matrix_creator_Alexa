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
#creator_mic_base_port = 20013+24

context = zmq.Context()
config_socket = context.socket(zmq.PUSH)
config_socket.connect('tcp://{0}:{1}'.format(creator_ip, creator_everloop_base_port))

recorded = False
servers = ["127.0.0.1:11211"]
mc = Client(servers, debug=1)
path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))


def setEverloopColor(red=0, green=0, blue=0, white=0, indice):
    config = driver_pb2.DriverConfig()
    image = []
    for led in range (35):

        if led == indice:
            ledValue = io_pb2.LedValue()
            ledValue.blue = blue
            ledValue.red = red
            ledValue.green = green
            ledValue.white = white
            image.append(ledValue)
        else :
            ledValue = io_pb2.LedValue()
            ledValue.blue = blue - abs(led - indice)*2
            ledValue.red = red -abs(led- indice)*2
            ledValue.green = green -abs(led - indice)*2
            ledValue.white = white - abs(led -indice)*2
            image.append(ledValue)

    config.image.led.extend(image)
    config_socket.send(config.SerializeToString())

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
        print "Debut du programme"
        #setEverloopColor(10,0,0,0)
        while True:
            capture_audio()
            setEverloopColor(10,10,0,0,20)
            time.sleep(2)
            setEverloopColor(10,10,10,0,10)
            time.sleep(2)
            setEverloopColor(0,0,10,0,30)
            time.sleep(2)
