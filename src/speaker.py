from machine import Pin, DAC, PWM

speaker_DAC = DAC(Pin(25, Pin.OUT), bits=12)

speaker_PWM = PWM(Pin(25, Pin.OUT), freq=0, duty=512)

