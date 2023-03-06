from machine import Pin, ADC
from time import *
from neopixel import NeoPixel

analog_pin = Pin(32, Pin.IN)
adc = ADC(analog_pin)
adc.atten(ADC.ATTN_11DB)

neopixel_pin = Pin(26, Pin.OUT)
neopixel_strip = NeoPixel(neopixel_pin, 30)
sensor_timer = ticks_ms()
analog_val_adjusted = 0
program_state = 'START'
calibration_val = 0
button_pin = Pin(39, Pin.IN)

def map_value(in_val, in_min, in_max, out_min, out_max):
    v = out_min + (in_val - in_min) * (out_max - out_min) / (in_max - in_min)
    if (v < out_min): 
        v = out_min 
    elif (v > out_max): 
        v = out_max
    return int(v)

while True:

    if(ticks_ms() > sensor_timer + 100):
        analog_val = adc.read()
        analog_val_8bit = map_value(analog_val, in_min = 0, in_max = 4095, out_min = 0, out_max = 255)
        print(analog_val)
        analog_val_25 = map_value(analog_val, 0, 4095, out_min = 0, out_max = 255)

        if(program_state == 'START'):
            if(button_pin.value() == 0):
                for pixel_index in range(25):
                    neopixel_strip[pixel_index] = (255,255,255)
                program_state = 'ON'
                print('change program_state to' + program_state)
            else:
                for pixel_index in range(25):
                    neopixel_strip[pixel_index] = (0,0,0)
            neopixel_strip.write()

        if(program_state == 'ON'):
            if (analog_val > 2500):
                for pixel_index in range(25):
                    neopixel_strip[pixel_index] = (0,0,0)
                program_state = 'START'
            else:
                for pixel_index in range(25):
                    neopixel_strip[pixel_index] = (255, 255, 255)
            neopixel_strip.write()
        sensor_timer = ticks_ms()
