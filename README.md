# SP23-Adv-Interactive-Prototyping   

## Introduction

My project is a crochet stand that helps people crochet in a more convenient way without having to struggle with the knots in the yarn. Based on my initial ideation, I was only going to use the servo motor to spin around the yarn to unwind, but as I was going through the process of user paint points in crocheting, I thought that it would make sense to have the user wind their yarn on first, then have a motion sensor on their wrist to automatically unwind the yarn for them.

## Implementation

### Hardware

1. light sensor (input)
2. angle unit (input)
3. LED strip light (output)
4. servo motor (output)
5. imu sensor (input)
6. two atom matrix boards

Schematic Diagram : https://drive.google.com/drive/folders/1YVtn1cUtS6EYl3XmPpTvg5JENjx6ec7n

### Firmware

Crochet Stand Code
* light sensor
* angle unit
* servo motor
* LED light strip

 ```
 from m5stack import *
 from time import *
 from machine import Pin, ADC
 from neopixel import NeoPixel
 from servo import Servo
 from libs.m5_espnow import *

 lightsensor_pin = Pin(33, Pin.IN)
 light_adc = ADC(lightsensor_pin)
 light_adc.atten(ADC.ATTN_11DB)

 anglesensor_pin = Pin(32, Pin.IN)
 angle_adc = ADC(anglesensor_pin)
 angle_adc.atten(ADC.ATTN_11DB)

 neopixel_pin = Pin(25, Pin.OUT)
 neopixel_strip = NeoPixel(neopixel_pin, 30)

 button_pin = Pin(39, Pin.IN)

 servo_obj = Servo(Pin(26))

 program_state = 'START'
 button_state = None
 tilt_val = 0

 sensor_timer = ticks_ms()

 local_mac = None
 peer_mac = None
 espnow = M5ESPNOW(1)


 local_mac = espnow.espnow_get_mac()

 def recv_cb(dummy):
     mac_addr, data_str = espnow.espnow_recv_str()
     if(':' in data_str):
         data_list = data_str.split(':')
         data_key = data_list[0]
         data_val = data_list[1]
         if(data_key == 'button'):
             global button_state
             button_state = 0
         if(data_key == 'tilt'):
             global tilt_val
             print('tilt = ' + data_val)
             tilt_val = data_val


 espnow.espnow_recv_cb(recv_cb)

 espnow.espnow_set_ap('M5_Receiver', '')

 print('waiting for messages from sender..')

 def map_value(in_val, in_min, in_max, out_min, out_max):
     v = out_min + (in_val - in_min) * (out_max - out_min) / (in_max - in_min)
     if (v < out_min): 
         v = out_min 
     elif (v > out_max): 
         v = out_max
     return int(v)

 while True:
     print(program_state)
     print(tilt_val)

     light_val = light_adc.read()
     light_val_8bit = map_value(light_val, in_min = 0, in_max = 4095, out_min = 0, out_max = 255)
     light_val_25 = map_value(light_val, 0, 4095, out_min = 0, out_max = 25)

     if(program_state == 'START'):
         if(light_val < 4000):
             for pixel_index in range(25):
                 neopixel_strip[pixel_index] = (90,90,90)
             program_state = 'WIND'
         else:
             for pixel_index in range(25):
                 neopixel_strip[pixel_index] = (0,0,0)
         neopixel_strip.write()

     if(program_state == 'WIND'):
         angle_val = angle_adc.read()
         servo_val = map_value(angle_val, 0, 4095, 1500, 1650)
         servo_obj.write_us(servo_val)
         print(servo_val)
         if(button_state == 0):
             servo_obj.write_us(1500)
             program_state = 'MOTOR'
             button_state = 1

     if(program_state == 'MOTOR'):
         if(light_val > 4000):
             program_state = 'DONE'
             for pixel_index in range(25):
                 neopixel_strip[pixel_index] = (0,0,0)
         if(tilt_val == "6"):
             print("Wind 2")
             servo_obj.write_us(1300)
             sleep_ms(500)
         else:
             servo_obj.write_us(1500)
             sleep_ms(2000)


     if(program_state == 'DONE'):
         servo_obj.write_us(1500)


     sleep_ms(100)
```
    
    
Wrist Band Code
* IMU sensor
* button
  
  ```
  from m5stack import *
  from time import *
  from machine import Pin, ADC
  from servo import Servo
  from easyIO import *
  import unit 
  import imu
  from neopixel import NeoPixel
  from libs.m5_espnow import *

  imu_sensor = imu.IMU()
  button_pin = Pin(39, Pin.IN)
  neopixel_pin = Pin(27, Pin.OUT)
  neopixel_strip = NeoPixel(neopixel_pin, 25)

  program_state = 'START'
  sensor_timer = ticks_ms()
  last_tilt_state = False
  current_tilt_state = False

  local_mac = None
  peer_mac = None
  tilt_val = 0 
  tilt_count = 0


  espnow = M5ESPNOW(1)  


  local_mac = espnow.espnow_get_mac()
  print('MAC address of this board: ', local_mac)


  while (peer_mac == None):
      print('scanning for peer board..')
      peer_mac = espnow.espnow_scan(1, 'M5_Receiver')
  print('MAC address of peer board: ', peer_mac)


  espnow.espnow_add_peer(peer_mac) 


  def send_cb(flag):
      if(flag == True):
          print('succeed!')
      else:
          print('failed..')


  espnow.espnow_send_cb(send_cb)  


  print('Wrist Board Initialized')
  neopixel_strip[0] = (0,0,0)

  while True:
      if(ticks_ms() > sensor_timer + 200):
          acc_x = imu_sensor.acceleration[0]
          if(tilt_count == 0):
              send_str = "tilt:0"
              print('sending.. ' + send_str)
              espnow.espnow_send_str(1, send_str)
          if(button_pin.value() == 0):
              send_str = "button:0"
              print('sending.. ' + send_str)
              espnow.espnow_send_str(1, send_str)
              program_state = 'MOTION'
          if(program_state == 'MOTION'):
              last_tilt_state = current_tilt_state
              if(0.5 <acc_x < 1.2):
                  current_tilt_state = True # is tilted
              else:
                  current_tilt_state = False

              if (last_tilt_state == False and current_tilt_state == True):
                  print("tilt:"+ str(tilt_count))
                  tilt_count += 1

              if(tilt_count == 1):
                  send_str = "tilt:1"
                  print('sending.. ' + send_str)
                  espnow.espnow_send_str(1, send_str)
                  for index in range(5):
                      neopixel_strip[index] = (90,90,90)
                      neopixel_strip.write()
                      sleep_ms(150)

              if(tilt_count == 2):
                  send_str = "tilt:2"
                  print('sending.. ' + send_str)
                  espnow.espnow_send_str(1, send_str)
                  for index in range(10):
                      neopixel_strip[index] = (90,90,90)
                      neopixel_strip.write()
                      sleep_ms(88)

              if(tilt_count == 3):
                  send_str = "tilt:3"
                  print('sending.. ' + send_str)
                  espnow.espnow_send_str(1, send_str)
                  for index in range(15):
                      neopixel_strip[index] = (90,90,90)
                      neopixel_strip.write()
                      sleep_ms(76)
              elif(tilt_count == 4):
                  send_str = "tilt:4"
                  print('sending.. ' + send_str)
                  espnow.espnow_send_str(1, send_str)
                  for index in range(20):
                      neopixel_strip[index] = (90,90,90)
                      neopixel_strip.write()
                      sleep_ms(64)
              elif(tilt_count== 5):
                  send_str = "tilt:5"
                  print('sending.. ' + send_str)
                  espnow.espnow_send_str(1, send_str)
                  for index in range(25):
                      neopixel_strip[index] = (90,90,90)
                      neopixel_strip.write()
                      sleep_ms(52)
              elif(tilt_count == 6):
                  send_str = "tilt:6"
                  print('sending.. ' + send_str)
                  espnow.espnow_send_str(1, send_str)
                  for index in range(25):
                      neopixel_strip[index] = (0,0,0)
                      neopixel_strip.write()
                      sleep_ms(100)
                  sleep_ms(1000)
                  tilt_count = 1
      neopixel_strip.write()
      ```
    
    
   ### Enclosure
   
   For the enclosure, 
