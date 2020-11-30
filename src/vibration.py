import uasyncio
from machine import Pin, PWM

class Vibration:
    def __init__(self):
        self.vibrating = False
        self.vibr_pin = PWM(Pin(33), freq=1000, duty=0)
        self.delay = 0
        self.intensity = 0

    def interpolate(self, x, in_min, in_max, out_min, out_max):
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def vibr(self, intensity):
        if intensity < 0:
            intensity = 0
        elif intensity > 1023:
            intensity = 1023
        self.vibr_pin.duty(intensity)

    async def success(self):
        if self.vibrating:
            return
        self.vibrating = True
        self.vibr(1023)
        await uasyncio.sleep_ms(200)
        self.vibr(500)
        await uasyncio.sleep_ms(200)
        self.vibr(1023)
        await uasyncio.sleep_ms(200)
        self.vibr(500)
        await uasyncio.sleep_ms(200)
        self.vibr(1023)
        await uasyncio.sleep_ms(200)
        self.vibr(500)
        await uasyncio.sleep_ms(200)
        self.vibr(0)
        self.vibrating = False

    async def failure(self):
        if self.vibrating:
            return
        self.vibrating = True
        self.vibr(1023)
        await uasyncio.sleep_ms(150)
        self.vibr(0)
        await uasyncio.sleep_ms(100)
        self.vibr(1023)
        await uasyncio.sleep_ms(150)
        self.vibr(0)
        self.vibrating = False

    async def heartbeat(self, distance):
        self.delay = self.interpolate(distance, 0, 50, 20, 1000)
        self.intensity = self.interpolate(distance, 0, 50, 950, 250)
        if self.vibrating:
            return
        self.vibrating = True
        if distance == 0:
            self.vibr(700)
            await uasyncio.sleep_ms(100)
            self.vibr(0)
            await uasyncio.sleep_ms(10)
        else:
            self.vibr(self.intensity)
            await uasyncio.sleep_ms(int(self.delay/2))
            self.vibr(0)
            await uasyncio.sleep_ms(int(self.delay/3))
            self.vibr(self.intensity)
            await uasyncio.sleep_ms(int(self.delay/2))
            self.vibr(0)
            await uasyncio.sleep_ms(self.delay)
        self.vibrating = False
