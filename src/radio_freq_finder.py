import math
import random
import uasyncio as asyncio
from speaker import speaker
from vibrate import success, failure

class RadioFreqFinder:
    def __init__(self, encoder, oled, next_puzzle):
        self.active = True
        self.encoder = encoder
        self.sineVals = []
        self.oled = oled
        self.next_puzzle = next_puzzle
        convFactor = (2*math.pi)/256
        for i in range(0, 256):
            radAngle = i*convFactor
            self.sineVals.insert(i, int((math.sin(radAngle)*127)+128))
        self.task = asyncio.create_task(self.tick())

    async def tick(self):
        skip = 0
        prev = None
        while self.active:
            curr_val = self.encoder.rotary_encoder.value()
            if not prev:
                prev = curr_val
            if skip >= 25 and prev != 0:
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
                ]
                try:
                    self.oled.fill(0)
                    curr_y = 0
                    for val in offset:
                        self.oled.text("_", curr_y * 10, 25 + val)
                        curr_y += 1
                    self.oled.show()
                except:
                    print("Screen write failed")
                skip = 0
                prev = curr_val
            if self.encoder.rotary_switch.value() == 0:
                if curr_val == 0:
                    asyncio.create_task(success())
                    self.active = False
                    self.encoder.rotary_encoder.set(min_val=0, max_val=3, value=0)
                    self.next_puzzle.active = True
                    self.next_puzzle.task = asyncio.create_task(self.next_puzzle.tick())
                    self.next_puzzle.next_puzzle = self
                else:
                    asyncio.create_task(failure())
            randHighOffset = random.randint(0, abs(curr_val))
            randLowOffset = random.randint(-abs(curr_val), 0)
            for x in range(200 + int(randLowOffset/2), 256):
                speaker.write(self.sineVals[x])
            for x in range(254, 200 + int(randHighOffset/2), -1):
                speaker.write(self.sineVals[x])
            skip += 1
            await asyncio.sleep_ms(1)