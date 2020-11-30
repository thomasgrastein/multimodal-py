import random
import uasyncio as asyncio

class Snake:
    def __init__(self, delay, peripherals, switch_puzzle):
        self.score = 1
        self.delay = delay
        self.peripherals = peripherals
        self.active = True
        self.snake = [(8, 4)]
        self.just_died = 11
        self.task = asyncio.create_task(self.tick())
        self.switch_puzzle = switch_puzzle

    def disable(self):
        self.active = False

    async def tick(self):
        food = (random.randint(0, 14), random.randint(0, 7))
        while self.active:
            direction = self.peripherals.encoder.rotary_encoder.value()
            # Input
            x, y = self.snake[0]
            if direction == 0:
                if y != 0:
                    self.snake.insert(0, (x, y - 1))
                else:
                    self.snake.insert(0, (x, int(self.peripherals.oled.height/8-1)))
            elif direction == 1:
                if x != int(self.peripherals.oled.width/8-1):
                    self.snake.insert(0, (x + 1, y))
                else:
                    self.snake.insert(0, (0, y))
            elif direction == 2:
                if y != int(self.peripherals.oled.height/8-1):
                    self.snake.insert(0, (x, y + 1))
                else:
                    self.snake.insert(0, (x, 0))
            elif direction == 3:
                if (x != 0):
                    self.snake.insert(0, (x - 1, y))
                else:
                    self.snake.insert(0, (int(self.peripherals.oled.width/8-1), y))

            # Feeding Check
            if food == (x, y):
                self.score += 1
                food_collides = True
                while food_collides:
                    food = (random.randint(0, int(self.peripherals.oled.width/8-2)),
                            random.randint(0, int(self.peripherals.oled.height/8-2)))
                    if food not in self.snake:
                        food_collides = False
                if self.delay > 10:
                    self.delay = self.delay - 10
                if self.score > 1:
                    try:
                        self.peripherals.oled.fill(0)
                        self.peripherals.oled.text("Squeeze", 10, 22)
                        self.peripherals.oled.show()
                    except:
                        print("Screen write failed")
                    await asyncio.sleep(1)
                    self.switch_puzzle(3)
                    break
            else:
                self.snake.pop()

            # Collision Check
            collide = False
            for point in self.snake[1:]:
                if point == self.snake[0]:
                    collide = True

            if collide and self.just_died >= 11:
                try:
                    self.peripherals.oled.fill(0)
                    self.peripherals.oled.text("Desynchronized", 10, 22)
                    self.peripherals.oled.show()
                except:
                    print("Screen write failed")
                asyncio.create_task(self.peripherals.vibration.failure())
                await asyncio.sleep(1)
                self.just_died = 0
                self.switch_puzzle(1)
                break

            if self.just_died < 11:
                self.just_died += 1

            try:
                self.peripherals.oled.fill(0)
                for point in self.snake:
                    self.peripherals.graphics.fill_rect(
                        point[0]*8, point[1]*8, 8, 8, self.just_died % 2)
                self.peripherals.graphics.fill_circle(food[0]*8+4, food[1]*8+4, 3, 1)
                self.peripherals.oled.show()
            except:
                print("Screen write failed")

            await asyncio.sleep_ms(self.delay)
