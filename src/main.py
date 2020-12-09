import uasyncio as asyncio
from pressure_sync import PressureSync
from radio_freq_finder import RadioFreqFinder
from snake import Snake
from peripherals import Peripherals
from networking import Network
import utime as time

class main:
    def __init__(self):
        self.peripherals = Peripherals()
        self.network = Network(self.peripherals, self.start, self.on_loose)
        self.first_puzzle = None
        self.second_puzzle = None
        self.third_puzzle = None
        self.task = asyncio.create_task(self.tick())
        self.error_count = 0
        self.started_at = 0
        self.peripherals.oled.text("Squeeze to start", 0, 28, 1)
        self.peripherals.oled.show()

    def switch_puzzle(self, puzzle):
        if self.first_puzzle:
            self.first_puzzle.disable()
        if self.second_puzzle:
            self.second_puzzle.disable()
        if self.third_puzzle:
            self.third_puzzle.disable()
        if puzzle == 0:
            self.first_puzzle.finish()
        if puzzle == 1:
            if self.first_puzzle:
                self.first_puzzle.active = True
                self.first_puzzle.task = asyncio.create_task(
                    self.first_puzzle.tick())
            else:
                self.first_puzzle = PressureSync(
                    self.peripherals, self.switch_puzzle, self.win, self.print_time, self.increment_error)
        elif puzzle == 2:
            self.peripherals.encoder.rotary_encoder.set(
                min_val=-50, max_val=50, range_mode=self.peripherals.encoder.rotary_encoder.RANGE_BOUNDED)
            if self.second_puzzle:
                self.second_puzzle.active = True
                self.second_puzzle.task = asyncio.create_task(
                    self.second_puzzle.tick())
            else:
                self.second_puzzle = RadioFreqFinder(
                    self.peripherals, self.switch_puzzle, self.print_time, self.increment_error)
        elif puzzle == 3:
            self.peripherals.encoder.rotary_encoder.set(
                min_val=0, max_val=3, value=0, range_mode=self.peripherals.encoder.rotary_encoder.RANGE_WRAP)
            if self.third_puzzle:
                self.third_puzzle.active = True
                self.third_puzzle.task = asyncio.create_task(
                    self.third_puzzle.tick())
            else:
                self.third_puzzle = Snake(
                    500, self.peripherals, self.switch_puzzle)

    def print_time(self, dif):
        curr_time = time.ticks_ms()
        print(str(curr_time - self.started_at) + "ms with", str(self.error_count), "errors") #str(dif), "took",
        self.error_count = 0
        self.started_at = curr_time

    def increment_error(self):
        self.error_count += 1

    def start(self):
        self.started_at = time.ticks_ms()
        self.switch_puzzle(1)
        self.network.state = "STARTED"

    def win(self):
        self.switch_puzzle(0)
        self.network.set_won()
        try:
            self.peripherals.oled.fill(0)
            self.peripherals.oled.text("You've won", 10, 10)
            self.peripherals.oled.show()
        except Exception as e:
            print(e)

    def on_loose(self):
        self.switch_puzzle(0)
        try:
            self.peripherals.oled.fill(0)
            self.peripherals.oled.text("You've lost", 10, 10)
            self.peripherals.oled.show()
        except Exception as e:
            print(e)

    async def tick(self):
        while True:
            if not self.first_puzzle and self.peripherals.fsr.read() > 500:
                self.start()
            await asyncio.sleep_ms(1000)

main = main()
asyncio.run(main.tick())
