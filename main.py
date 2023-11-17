import pygame

pygame.init()

SCREEN_SIZE = (1000, 500)


screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Nordic_Journey")


class ImageChanger:
    def __init__(self, img):
        self.img = img

    def get_image(self, frame, width, height, padding, scale, color):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.img, (0, 0), ((frame * (width + padding)), 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(color)

        return image


class Animation(pygame.sprite.Sprite):
    def __init__(self, img, steps=[], cooldown=0, loop=True, width=0, height=0, padding=0):
        self.sprite_sheet = ImageChanger(pygame.image.load(img).convert_alpha())
        self.steps = steps
        self.frames = [
            self.sprite_sheet.get_image(i, width, height, padding, 3, BLACK)
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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, idle_animation = None, x = 0, y = 0):
        if idle_animation:
            self.animation = {'idle':idle_animation}
        self.velocity = [0, 0]
        self.x = x
        self.y = y
        self.dir = 1
        self.modes = ['idle']
        self.mode = 'idle'

    def update(self):
        for mode in self.modes:
            if mode != self.mode:
                self.animation[mode].reset()
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.animation[self.mode].update()
        if self.velocity[0] < 0:
            self.dir = 0
        elif self.velocity[0] > 0:
            self.dir = 1
        if self.velocity[1] > 0:
            self.velocity[1] -= GRAVITY

        screen.blit(self.animation[self.mode].image if self.dir else pygame.transform.flip(self.animation[self.mode].image.convert_alpha(), True, False), (self.x, self.y))

    def add_animation(self, animation, mode):
        self.animation[mode] = animation
        self.modes.append(mode)

BG = (50, 50, 50)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()
FPS = 60
VELOCITY = 4
GRAVITY = 0.5

King = AnimatedSprite(Animation("src/King/idle.png", [7] * 11, 0, True, 63, 58, 15), 100, 100)
King.add_animation(Animation("src/King/run.png", [6] * 8, 0, True, 63, 58, 15), "run")

def King_mode(King):
    if King.velocity[0] == 0:
        King.mode = 'idle'
    else:
        King.mode = 'run'

run = True
while run:
    clock.tick(FPS)
    screen.fill(BG)
    # print(King.step_idx)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            # print(event.key)
            if event.key == pygame.K_ESCAPE:
                run = False
            elif event.key == pygame.K_LEFT:
                King.velocity[0] += -VELOCITY
            elif event.key == pygame.K_RIGHT:
                King.velocity[0] += VELOCITY
            elif event.key == pygame.K_UP:
                King.velocity[1] += -VELOCITY
        elif event.type == pygame.KEYUP:
            # print(event.key, "up")
            if event.key == pygame.K_LEFT:
                King.velocity[0] += VELOCITY
            elif event.key == pygame.K_RIGHT:
                King.velocity[0] -= VELOCITY
    King_mode(King)
    King.update()
    # print(King.rect.x, King.rect.y)
    pygame.display.update()

pygame.quit()
