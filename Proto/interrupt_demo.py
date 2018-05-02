#!/usr/bin/python
# modified by Waune Seltzer
# script by Alex Eames http://RasPi.tv
# http://RasPi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3

import sys
import time 
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

# set up as inputs, pulled up to avoid false detection.
# Both ports are wired to connect to GND on button press.
# So we'll be setting up falling edge detection for both

ledpin = 13
whitebuttonpin = 12
redbuttonpin = 15
pirpin = 11
GPIO.setup(ledpin, GPIO.OUT)
GPIO.setup(whitebuttonpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(redbuttonpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pirpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(ledpin, GPIO.LOW)  # turn on LED

# now we'll define two threaded callback functions
# these will run in another thread when our events are detected
def my_callback_whitebutton(channel):
    print ("white button pressed")

def my_callback_redbutton(channel):
    print ("red button pressed")

def my_callback_pir(channel):
    print ("motion detected")

# when a falling edge is detected on buttonpin, regardless of whatever 
# else is happening in the program, the function my_callback_button will be run
GPIO.add_event_detect(whitebuttonpin, GPIO.FALLING, callback=my_callback_whitebutton, bouncetime=300)
GPIO.add_event_detect(redbuttonpin, GPIO.FALLING, callback=my_callback_redbutton, bouncetime=300)
GPIO.add_event_detect(pirpin, GPIO.FALLING, callback=my_callback_pir, bouncetime=300)

while True:
    try:
        #print("Waiting for interrupts...")
        time.sleep(1)   # Delay for 1 second 
        GPIO.output(ledpin, GPIO.LOW)  # LED on
        time.sleep(1)
        GPIO.output(ledpin, GPIO.HIGH)  # LED off
    except KeyboardInterrupt:
        # quit
        print("Exiting")
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
        sys.exit()
