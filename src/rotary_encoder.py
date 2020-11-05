import uasyncio as asyncio
from machine import Pin
from rotary_irq_esp import RotaryIRQ


class RotaryEncoder:
    def __init__(self):
        self.rotary_encoder = RotaryIRQ(pin_num_clk=0,
                                        pin_num_dt=4,
                                        min_val=-50,
                                        max_val=50,
                                        reverse=False,
                                        range_mode=RotaryIRQ.RANGE_WRAP
                                        )
        self.rotary_switch = Pin(32, Pin.IN, Pin.PULL_UP)

