import uasyncio as asyncio
import random
from utime import sleep_ms

in_min = 0
in_max = 3800
out_min = 64
out_max = 0

class PressureSync:
    def __init__(self, peripherals, switch_puzzle, win, print_time, increment_error):
        self.peripherals = peripherals
        self.switch_puzzle = switch_puzzle
        self.active = True
        self.level = 0
        self.interrupted = True
        self.win = win
        self.finished = False
        values_for_seed = ""
        while True:
            if len(values_for_seed) == 0:
                values_for_seed += str(self.peripherals.fsr.read())[1:]
            else:
                values_for_seed += str(self.peripherals.fsr.read())
            if len(values_for_seed) > 15:
                break
            sleep_ms(5)
        print("True random seed:", values_for_seed)
        random.seed(int(values_for_seed))
        self.offset = [
            int(random.randint(0, 45)),
            int(random.randint(0, 30)),
            int(random.randint(30, 45))
        ]
        print("First offset:", self.offset[0])
        self.task = asyncio.create_task(self.tick())
        self.print_time = print_time
        self.increment_error = increment_error

    def interpolate(self, x):
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def disable(self):
        self.active = False

    def finish(self):
        self.finished = True

    async def tick(self):
        if not self.interrupted:
            if self.level >= 2:
                self.win()
                return
            else:
                self.level += 1
        while self.active:
            y = self.interpolate(self.peripherals.fsr.read())
            try:
                self.peripherals.oled.fill(0)
                curr_x = 0
                for offset_y in self.offset:
                    self.peripherals.graphics.rect(curr_x, 0, 11, 64, 1)
                    self.peripherals.graphics.rect(curr_x, offset_y, 11, 15, 1)
                    curr_x += int(128/2-8)
                self.peripherals.graphics.fill_circle(5 + self.level * int(128/2-8), y, 2, 1)
                self.peripherals.oled.show()
            except Exception as e:
                print("Screen write failed", e)
            if self.offset[self.level] <= y <= self.offset[self.level] + 15:
                self.switch_puzzle(2)
                self.interrupted = False
            await asyncio.sleep_ms(20)
        while not self.active and not self.finished:
            reading = self.interpolate(self.peripherals.fsr.read())
            if reading > self.offset[self.level] + 15 or reading < self.offset[self.level]:
                self.interrupted = True
                self.increment_error()
                self.switch_puzzle(1)
            await asyncio.sleep_ms(50)
