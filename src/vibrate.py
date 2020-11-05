import uasyncio
from machine import Pin, PWM
vibr_pin = PWM(Pin(33), freq=1000, duty=0)


def vibr(intensity):
    if intensity < 0:
        intensity = 0
    elif intensity > 1023:
        intensity = 1023
    vibr_pin.duty(intensity)


async def success():
    vibr(1023)
    await uasyncio.sleep_ms(200)
    vibr(500)
    await uasyncio.sleep_ms(200)
    vibr(1023)
    await uasyncio.sleep_ms(200)
    vibr(500)
    await uasyncio.sleep_ms(200)
    vibr(1023)
    await uasyncio.sleep_ms(200)
    vibr(500)
    await uasyncio.sleep_ms(200)
    vibr(0)

async def failure():
    vibr(1023)
    await uasyncio.sleep_ms(150)
    vibr(0)
    await uasyncio.sleep_ms(100)
    vibr(1023)
    await uasyncio.sleep_ms(150)
    vibr(0)
