import random
import uasyncio as asyncio
from vibrate import failure

class Snake:
    def __init__(self, delay, oled, graphics, encoder):
        self.score = 1
        self.delay = delay
        self.oled = oled
        self.graphics = graphics
        self.encoder = encoder
        self.active = False
        self.next_puzzle = None
        self.snake = [(8, 4)]
        self.just_died = 11
        self.task = asyncio.create_task(self.tick())

    async def tick(self):
        food = (random.randint(0, 14), random.randint(0, 7))
        while self.active:
            direction = self.encoder.rotary_encoder.value()
            # Input
            x, y = self.snake[0]
            if direction == 0:
                if y != 0:
                    self.snake.insert(0, (x, y - 1))
                else:
                    self.snake.insert(0, (x, int(self.oled.height/8-1)))
            elif direction == 1:
                if x != int(self.oled.width/8-1):
                    self.snake.insert(0, (x + 1, y))
                else:
                    self.snake.insert(0, (0, y))
            elif direction == 2:
                if y != int(self.oled.height/8-1):
                    self.snake.insert(0, (x, y + 1))
                else:
                    self.snake.insert(0, (x, 0))
            elif direction == 3:
                if (x != 0):
                    self.snake.insert(0, (x - 1, y))
                else:
                    self.snake.insert(0, (int(self.oled.width/8-1), y))

            # Feeding Check
            if food == (x, y):
                self.score += 1
                food_collides = True
                while food_collides:
                    food = (random.randint(0, int(self.oled.width/8-2)),
                            random.randint(0, int(self.oled.height/8-2)))
                    if food not in self.snake:
                        food_collides = False
                if self.delay > 10:
                    self.delay = self.delay - 10
            else:
                self.snake.pop()

            # Collision Check
            collide = False
            for point in self.snake[1:]:
                if point == self.snake[0]:
                    collide = True

            if collide and self.just_died >= 11:
                self.active = False
                self.encoder.rotary_encoder.set(
                    min_val=-50, max_val=50, value=random.randint(-50, 50))
                self.next_puzzle.active = True
                try:
                    self.oled.fill(0)
                    self.oled.text("Desynchronized", 10, 22)
                    self.oled.show()
                except:
                    print("Screen write failed")
                asyncio.create_task(failure())
                await asyncio.sleep(1)
                self.next_puzzle.task = asyncio.create_task(
                    self.next_puzzle.tick())
                self.next_puzzle.next_puzzle = self
                self.just_died = 0
                break

            if self.just_died < 11:
                self.just_died += 1

            try:
                self.oled.fill(0)
                for point in self.snake:
                    self.graphics.fill_rect(
                        point[0]*8, point[1]*8, 8, 8, self.just_died % 2)
                self.graphics.fill_circle(food[0]*8+4, food[1]*8+4, 3, 1)
                self.oled.show()
            except:
                print("Screen write failed")

            await asyncio.sleep_ms(self.delay)
