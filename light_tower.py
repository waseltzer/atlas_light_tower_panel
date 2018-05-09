#!/usr/bin/python -u

# ATLAS Institute Light Tower Panel project
# https://github.com/waseltzer/atlas_light_tower_panel
# http://btulab.com/atlas-tower-light
# sergio.rivera@colorado.edu
# wayne.seltzer@colorado.edu

import sys
import time
import RPi.GPIO as GPIO
import requests
import pprint
import subprocess

# Hardware connections:
GPIO.setmode(GPIO.BOARD) #use board pin numbers

ledpin = 13
whitebuttonpin = 12
pirpin = 11
redbuttonpin = 15

GPIO.setup(ledpin, GPIO.OUT)
# set up as inputs, pulled up to avoid false detection.
# Both ports are wired to connect to GND on button press.
# So we'll be setting up falling edge detection for both
GPIO.setup(whitebuttonpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pirpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(redbuttonpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ATLAS Light Tower API
# from: https://github.com/slsp8752/atlas-tower-light-controller
# Key frames are sent as a series of values separated by single letter markers. In order, they are:
#
# k: key frame number (0 through 9)
# r: color; red value (000 through 255)
# g: color; green value (000 through 255)
# b: color; blue value (000 through 255)
# m: transition mode (1 for 'snap' 2 for 'fade')
# t: duration (00000 through 10000 milliseconds)
# F: denotes the last frame in a set of key frames.
# A full key frame looks like this:
#
# k0r255g000b127m1t01000
# or like this if it's the last frame in a set:
# k0r255g000b127m1t01000F

# api-endpoint
URL = "https://atlas-tower.herokuapp.com/keyStatus"

keyframes = {
	'red': {'frame':'k0r255g000b000m2t01000F'},
	'green': {'frame':'k0r000g255b000m2t01000F'},
	'blue': {'frame':'k0r000g000b255m2t01000F'},
	'white': {'frame':'k0r255g255b255m2t01000F'},
	'red blue': {'frame':'k0r255g000b000m2t03000k1r000g000b255m2t03000F'},
	'white blue': {'frame':'k0r255g255b255m2t01000k1r000g000b255m2t01000F'},
	'red green': {'frame':'k0r255g000b000m2t01000k1r000g255b000m2t01000F'},
	'red white': {'frame':'k0r255g000b000m1t00500k1r255g255b255m1t00500F'},
	'white white flash ': {'frame':'k0r255g255b255m1t00100k1r000g000b000m1t00100F'},
	'off': {'frame':'k0r000g000b000m2t01000F'}
}

def send_to_light_tower(kf):
    keyframe = keyframes[kf]
    print("Sending " + kf + " to light tower...", end=' ',flush=True)
    # sending get request and saving the response as response object
    r = requests.get(url = URL, params = keyframe, timeout=20.00)
    # printing the output
    #print('Response: ' + r.text)
    #print('Status code: ' + str(r.status_code))
    print('Error code: ' + str(r.raise_for_status()))

def speak(s,wait):  # espeak string s, wait for audio to complete if wait is True
    cmd = 'espeak \"' + s + '\" ' + '-s120 -vmb-us1 --stdout | aplay -q -D sysdefault:CARD=1'
    p = subprocess.Popen([cmd], shell=True)
    if wait: # wait for audio to complete
        p.wait()

def log(s):  # print the current timestamp and string
    print(time.asctime(time.localtime(time.time())) + " " + s)

# setup hardware interrupts for buttons and PIR
# based on Python interrupts tutorial
# http://RasPi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3

# define threaded callback functions
# these will run in another thread when our events are detected

def my_callback_whitebutton(channel):
    global keyframekey
    log("white button pressed")
    kf = list(keyframes.keys())[keyframekey]
    speak('Setting lights to ' + kf,False)
    send_to_light_tower(list(keyframes.keys())[keyframekey])
    speak('Done',True)

def my_callback_pir(channel):
#    log("motion detected")
    subprocess.Popen(['aplay -q -D sysdefault:CARD=1 /home/pi/Code/sonar-ping.wav'], shell=True)

keyframekey=0
def my_callback_redbutton(channel):
    global keyframekey
    log("red button pressed")
    keyframekey = keyframekey + 1
    if (keyframekey == len(keyframes)):
        keyframekey = 0
    kf = list(keyframes.keys())[keyframekey]
    print("Color: ", kf)
    speak('Color ' + kf,True)

# when a falling edge is detected on buttonpin, regardless of whatever
# else is happening in the program, the function my_callback_button will be run
GPIO.add_event_detect(whitebuttonpin, GPIO.FALLING,callback=my_callback_whitebutton, bouncetime=1000)
GPIO.add_event_detect(pirpin, GPIO.FALLING, callback=my_callback_pir, bouncetime=10000)
GPIO.add_event_detect(redbuttonpin, GPIO.FALLING, callback=my_callback_redbutton, bouncetime=500)

# Main program
print ("===================================================================================================")
log("Light Tower startup")

# turn on LED
GPIO.output(ledpin, GPIO.LOW)

# Set the sound volume level
subprocess.Popen(['amixer -q -c 1 set PCM -- 190'], shell=True)
  
# set an initial light tower keyframe
send_to_light_tower('red green') #set initial keyframes

while True:
    try:
        #blink the LED
        time.sleep(1)   # Delay for 1 second
        GPIO.output(ledpin, GPIO.LOW)  # LED on
        time.sleep(1)
        GPIO.output(ledpin, GPIO.HIGH)  # LED off
    except KeyboardInterrupt:
        # quit
        print("Exiting")
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
        sys.exit()
