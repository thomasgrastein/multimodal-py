import math
import random
import uasyncio as asyncio
from machine import Pin, PWM, DAC
speaker = DAC(Pin(25, Pin.OUT), bits=12)

class disabled:
    def __init__(self):
        self.display = True
        self.speaker = False
        self.vibration = False
        self.difficulty = 0

    def set_difficulty(self, val):
        self.difficulty = val
        if val == 0:
            self.display = False
            self.speaker = False
            self.vibration = False
        elif val == 1:
            self.display = True
            self.speaker = False
            self.vibration = False
        elif val == 2:
            self.display = True
            self.speaker = False
            self.vibration = True

class RadioFreqFinder:
    def __init__(self, peripherals, switch_puzzle, print_time, increment_error):
        self.active = True
        self.peripherals = peripherals
        self.sineVals = []
        self.disabled = disabled()
        convFactor = (2*math.pi)/256
        for i in range(0, 256):
            radAngle = i*convFactor
            self.sineVals.insert(i, int((math.sin(radAngle)*127)+128))
        self.task = asyncio.create_task(self.tick())
        self.switch_puzzle = switch_puzzle
        self.print_time = print_time
        self.increment_error = increment_error
        self.was_correct = False

    def disable(self):
        self.active = False

    async def tick(self):
        skip = 0
        prev = None
        while self.active:
            curr_val = self.peripherals.encoder.rotary_encoder.value()
            if self.was_correct and curr_val != 0:
                self.increment_error()
                self.was_correct = False
            elif curr_val == 0:
                self.was_correct = True
            if not prev:
                prev = curr_val
            if skip >= 25 and curr_val == 0 and not self.disabled.display:
                try:
                    self.peripherals.oled.fill(0)
                    self.peripherals.graphics.line(
                        0, 32, 128, 32, 1)
                    self.peripherals.oled.show()
                except Exception as e:
                    print("Screen write failed:", e)
                skip = -100
                prev = curr_val
            elif skip >= 25 and prev != 0:
                if not self.disabled.display:
                    val = curr_val
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
                        int(random.randint(-31, 31) * val),
                    ]
                    try:
                        self.peripherals.oled.fill(0)
                        for i in range(0, 13):
                            self.peripherals.graphics.line(
                                i*10, 32 + offset[i], i*10+10, 32 + offset[i+1], 1)
                        self.peripherals.oled.show()
                    except Exception as e:
                        print("Screen write failed:", e)
                else:
                    self.peripherals.oled.fill(0)
                    self.peripherals.oled.show()
                skip = 0
                prev = curr_val
            if self.peripherals.encoder.rotary_switch.value() == 0:
                if curr_val == 0:
                    self.switch_puzzle(1)
                    self.print_time(self.disabled.difficulty)
                    #self.disabled.set_difficulty(self.disabled.difficulty + 1)
                    self.peripherals.encoder.rotary_encoder.set(
                        value=random.randint(-50, 50))
                else:
                    self.increment_error()
                    await asyncio.sleep_ms(1000)
            if not self.disabled.speaker:
                amount = 5
                if curr_val == 0:
                    randHighOffset = 0
                    randLowOffset = 0
                    amount = 6
                elif abs(curr_val) == 1:
                    randHighOffset = random.randint(0, 5)
                    randLowOffset = random.randint(-5, 0)
                else:
                    randHighOffset = random.randint(0, abs(curr_val)*2)
                    randLowOffset = random.randint(-abs(curr_val)*2, 0)

                for x in range(0 + randHighOffset, 255 + randLowOffset, +amount):
                    try:
                        speaker.write(self.sineVals[x])
                    except Exception as e:
                        print(e, x)
            skip += 1
            if not self.disabled.vibration:
                asyncio.create_task(
                    self.peripherals.vibration.heartbeat(abs(curr_val)))
            await asyncio.sleep_ms(1)
