import pygame

BLACK = (0, 0, 0)

class ImageChanger:
    def __init__(self, img):
        self.img = img

    def get_image(self, frame, width, height, padding, scale, color, dir = 1):
        image = pygame.Surface((width, height)).convert_alpha()
        if dir == 2:image.blit(self.img, (0, 0), (0, (frame * (height + padding)), width, height))
        else: image.blit(self.img, (0, 0), ((frame * (width + padding)), 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(color)

        return image


class Animation(pygame.sprite.Sprite):
    def __init__(self, img, steps=[], cooldown=0, loop=True, width=0, height=0, padding=0, d=1):
        self.sprite_sheet = ImageChanger(pygame.image.load(img).convert_alpha())
        self.steps = steps
        self.frames = [
            self.sprite_sheet.get_image(i, width, height, padding, 3, BLACK, d)
            for i in range(len(steps))
        ]
        self.step_idx = 0
        self.current_frame = 0
        self.cooldown = cooldown
        self.loop = loop
        self.image = self.frames[self.current_frame]
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.current_frame += 1
        if self.current_frame >= self.steps[self.step_idx]:
            self.current_frame = 0
            self.step_idx += 1
            if self.step_idx >= len(self.steps):
                self.step_idx = 0 if self.loop else len(self.steps) - 1

        self.image = self.frames[self.step_idx]

    def reset(self):
        self.step_idx = 0
        self.current_frame = 0
        # screen.blit(self.image, (self.x, self.y))

class AnimGroup:
    def __init__(self):
        self.__sprites = []

    def update(self):
        for i in self.__sprites:
            i.update()
            if i.death < 0:
                self.__sprites.remove(i)
    
    def do(self, fun):
        for i in self.__sprites:
            exec(f"i.{fun}()")

    def add(self, sprite):
        self.__sprites.append(sprite)

    def __iter__(self):
        return iter(self.__sprites)
