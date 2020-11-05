from machine import Pin, DAC

speaker = DAC(Pin(25, Pin.OUT), bits=12)
