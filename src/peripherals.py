from machine import Pin, ADC, I2C
from rotary_encoder import RotaryEncoder
import random
import ssd1306
import gfx
from vibration import Vibration

class Peripherals:
    def __init__(self):
        self.fsr = ADC(Pin(34))
        self.fsr.atten(ADC.ATTN_11DB)
        self.encoder = RotaryEncoder()
        self.oled = ssd1306.SSD1306_I2C(
            128, 64, I2C(-1, scl=Pin(22), sda=Pin(21)))
        self.graphics = gfx.GFX(128, 64, self.oled.pixel)
        self.encoder.rotary_encoder.set(value=random.randint(-50, 50))
        self.vibration = Vibration()
