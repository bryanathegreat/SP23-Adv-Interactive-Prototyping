from m5stack import *
from machine import Pin
from time import *

led_pin = Pin(32, Pin.OUT)
button_pin = Pin(26, Pin.IN, Pin.PULL_UP)

while True:
  if(button_pin.value() == 0):
    led_pin.on() 
    print("led")
  else:
    led_pin.off()  
    print("ledOff")
  sleep_ms(100)
