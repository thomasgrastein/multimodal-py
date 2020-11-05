import gfx
import uasyncio as asyncio
from machine import Pin, ADC, I2C
import ssd1306
import random
#from screen import noiseScreen, updateScreen, updateLine
#from speaker import speaker
from rotary_encoder import RotaryEncoder
from radio_freq_finder import RadioFreqFinder
from snake import Snake

class main:
    def __init__(self):
        self.fsr = ADC(Pin(34))
        self.fsr.atten(ADC.ATTN_11DB)
        self.rotary_encoder = RotaryEncoder()
        self.oled = ssd1306.SSD1306_I2C(128, 64, I2C(-1, scl=Pin(22), sda=Pin(21)))
        self.graphics = gfx.GFX(128, 64, self.oled.pixel)
        self.correct_channel = 0
        self.current_puzzle = 1
        self.task = asyncio.create_task(self.tick())
        self.rotary_encoder.rotary_encoder.set(value=random.randint(-50, 50))
        self.second_puzzle = Snake(500, self.oled, self.graphics, self.rotary_encoder)
        self.first_puzzle = RadioFreqFinder(self.rotary_encoder, self.oled, self.second_puzzle)
    async def tick(self):
        while True:
            #Keep alive
            await asyncio.sleep_ms(500)

main = main()
asyncio.run(main.tick())
