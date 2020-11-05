import random
from machine import Pin, I2C
import ssd1306

lines = ["Welcome", "Find the channel","","","",""]

def updateLine(index, text):
    lines[index] = text

async def updateScreen():
    oled.fill(0)
    currY = 0
    for text in lines:
        oled.text(text, 0, currY)
        currY += 10
    oled.show()

async def noiseScreen(val):
    if abs(val) == 1:
        val = 0.05
    elif val == 0:
        val = 0
    else:
        val = val/50
    offset = [
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
        int(random.randint(-31, 31) * val),
    ]

    oled.fill(0)
    oled.text("_", 0, 25 + offset[0])
    oled.text("_", 10, 25 + offset[1])
    oled.text("_", 20, 25 + offset[2])
    oled.text("_", 30, 25 + offset[3])
    oled.text("_", 40, 25 + offset[4])
    oled.text("_", 50, 25 + offset[5])
    oled.text("_", 60, 25 + offset[6])
    oled.text("_", 70, 25 + offset[7])
    oled.text("_", 80, 25 + offset[8])
    oled.text("_", 90, 25 + offset[9])
    oled.text("_", 100, 25 + offset[10])
    oled.text("_", 110, 25 + offset[11])
    oled.text("_", 120, 25 + offset[12])
    oled.show()

updateScreen()
