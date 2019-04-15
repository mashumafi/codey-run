import codey, event
from random import randint
from math import floor

class Point(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def update(self, speed: float):
        self.x -= speed

    def draw(self, canvas: Canvas):
        canvas.set_pixel(self.x, self.y, True)

    def is_visible(self) -> bool:
        return self.x >= 0

class Canvas(object):
    def __init__(self):
        self.front_buffer = set()
        self.back_buffer = set()

    def draw(self):
        common = self.front_buffer | self.back_buffer
        remove = common - self.back_buffer
        insert = common - self.front_buffer
        for point in remove:
            codey.display.set_pixel(point.x, point.y, False)
        for point in insert:
            codey.display.set_pixel(point.x, point.y, True)
        self.front_buffer = self.back_buffer
        self.back_buffer = set()

    def set_pixel(self, x: int, y: int, on: bool):
        point = Point(floor(x), floor(y))
        if on:
            self.back_buffer.add(point)
        elif point in self.back_buffer:
            self.back_buffer.remove(point)

class Player(object):
    RUNNING = 0
    DUCKING = 1
    JUMPING = 2
    FALLING = 3
    DEAD    = 4

    def __init__(self):
        self.state = Player.RUNNING
        self.y = 5

    def update(self, dt: float):
        if self.state == Player.RUNNING:
            if codey.button_a.is_pressed():
                self.state = Player.DUCKING
                codey.speaker.play_melody('exhaust.wav')
            if codey.button_b.is_pressed():
                self.state = Player.JUMPING
                codey.speaker.play_melody('jump.wav')
        if self.state == Player.DUCKING:
            if not codey.button_a.is_pressed():
                self.state = Player.RUNNING
        if self.state == Player.JUMPING:
            if not codey.button_b.is_pressed():
                self.state = Player.FALLING
            else:
                self.y -= 8 * dt
                if self.y <= 3:
                    self.state = Player.FALLING
                    self.y = 3
        if self.state == Player.FALLING:
            self.y += 6 * dt
            if self.y >= 5:
                self.state = Player.RUNNING
                self.y = 5

    def draw(self, canvas: Canvas):
        is_standing = self.state != Player.DUCKING
        canvas.set_pixel(2, self.y, is_standing)
        canvas.set_pixel(2, self.y + 1, is_standing)
        canvas.set_pixel(2, self.y + 2, True)
    
    def is_colliding(self, point: Point):
        if floor(point.x) == 2:
            if self.state == Player.DUCKING:
                return point.y == 7
            elif self.state == Player.JUMPING or self.state == Player.FALLING:
                return point.y == 5
            elif self.state == Player.RUNNING:
                return True
        return False

class Button(object):
    def __init__(self, is_pressed):
        self.__test = is_pressed
        self.__is_pressed = is_pressed()
        self.__was_just_pressed = self.__is_pressed
    
    def update(self):
        is_pressed = self.__test()
        self.__was_just_pressed = is_pressed and not self.__is_pressed
        self.__is_pressed = is_pressed
        
    def is_pressed(self):
        return self.__is_pressed
    
    def was_just_pressed(self):
        return self.__was_just_pressed

c_button = Button(codey.button_c.is_pressed)

class Game(object):
    TITLE = 0
    PLAYING = 1
    PAUSED = 2
    SCORE = 3
    
    def __init__(self):
        self.state = Game.TITLE
        self.player = Player()
        self.score = 0
        self.obstacle = None
        self.canvas = Canvas()

    def update(self, dt: float):
        c_button.update()
        if self.state == Game.TITLE or self.state == Game.SCORE:
            if codey.button_a.is_pressed() or codey.button_b.is_pressed():
                self.state = Game.TITLE
            if c_button.was_just_pressed():
                self.state = Game.PLAYING
                self.score = 0
                self.obstacle = None
                codey.display.clear()
        elif self.state == Game.PLAYING:
            if c_button.was_just_pressed():
                self.state = Game.PAUSED
                return
            self.player.update(dt)
            if self.obstacle is None:
                self.obstacle = Point(16, 5 + randint(0, 1) * 2)
            self.obstacle.update(dt * (4 + min(self.score / 2, 8)))
            if self.player.is_colliding(self.obstacle):
                codey.speaker.play_melody('hurt.wav')
                self.state = Game.SCORE
            if not self.obstacle.is_visible():
                self.obstacle = None
                self.score += 1
        elif self.state == Game.PAUSED:
            if c_button.was_just_pressed():
                self.state = Game.PLAYING
                codey.display.clear()
                return
            codey.display.show_image("00007e7e7e7e000000007e7e7e7e0000")

    def draw(self):
        if self.state == Game.TITLE:
            codey.display.show('run', wait = True)
        elif self.state == Game.PLAYING:
            self.player.draw(self.canvas)
            if self.obstacle:
                self.obstacle.draw(self.canvas)
            self.canvas.draw()
        elif self.state == Game.SCORE:
            codey.display.show(self.score, wait = True)

@event.start
def on_start():
    game = Game()
    start = codey.get_timer()
    while True:
        current = codey.get_timer()
        game.update(current - start)
        game.draw()
        start = current
