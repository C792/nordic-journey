import pygame
import random
pygame.init()

SCREEN_SIZE = (960, 576)

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Nordic Journey")

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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, idle_animation = None, x = 0, y = 0, health = 100):
        if idle_animation:
            self.animation = {'idle':idle_animation}
        self.velocity = [0, 0]
        self.x = x
        self.y = y
        self.jump = 0
        self.attack = 0
        self.damage = 0
        self.death = 0
        self.health = health
        self.dir = 1
        self.modes = ['idle']
        self.mode = 'idle'
        self.imgsize = (0, 0)
        self.rect = pygame.Rect(self.x, self.y, self.imgsize[0], self.imgsize[1])
        self.image = self.animation[self.mode].image

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
        if self.jump:
            self.velocity[1] += GRAVITY
            self.jump -= 1
        else:
            self.jump = 0
            self.velocity[1] = 0
        if self.y > GROUND:
            self.y = GROUND
            self.velocity[1] = 0
            self.jump = 0
        if self.attack:
            self.attack -= 1
        if self.damage:
            self.damage -= 1
        if self.health <= 0 and self.death == 0:
            self.death = sum(self.animation["death"].steps) + 90
            self.attack = 0
        if self.death > 0:
            self.attack = 0
            self.death -= 1
            if self.death == 0:
                self.death -= 1
                return
        self.rect = pygame.Rect(self.x + self.image.get_width()  / 2 - self.imgsize[0] * 1.6,
                                self.y + self.image.get_height() / 2 - self.imgsize[1] * 1.6,
                                self.imgsize[0] * 3.2,
                                self.imgsize[1] * 3.2)
        # print(self.x - self.imgsize[0] / 2, self.y - self.imgsize[1] / 2, self.imgsize[0], self.imgsize[1])
        self.image = self.animation[self.mode].image if self.dir else pygame.transform.flip(self.animation[self.mode].image.convert_alpha(), True, False)
        screen.blit(self.image, (self.x, self.y))
        # pygame.draw.rect(screen, (0, 255, 0), self.rect)

    def add_animation(self, animation, mode):
        self.animation[mode] = animation
        self.modes.append(mode)

class Tile(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(img).convert_alpha(), (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class TreeMonster(AnimatedSprite):
    def __init__(self, x=0, y=0, health=40):
        super().__init__(Animation("src/TreeMonster/idle.png", [15] * 4, 0, True, 96, 96, 0, 2), x, y, health)
        # TM = AnimatedSprite(Animation("src/TreeMonster/idle.png", [15] * 4, 0, True, 96, 96, 0, 2), 300, GROUND - TM_PADDING)
        self.walk = 0
        self.damage = 0
        self.imgsize = (49, 61)
        self.walk_cooldown = 0
        self.add_animation(Animation("src/TreeMonster/run.png", [10] * 5, 0, True, 96, 96, 0, 2), "walk")
        self.add_animation(Animation("src/TreeMonster/run.png", [5] * 5, 0, True, 96, 96, 0, 2), "run")
        self.add_animation(Animation("src/TreeMonster/attack.png", [4] * 6, 0, True, 96, 96, 0, 2), "attack")
        self.add_animation(Animation("src/TreeMonster/damage.png", [2, 2, 3, 3, 3], 0, False, 96, 96, 0, 2), "damage")
        self.add_animation(Animation("src/TreeMonster/death.png", [5] * 8, 0, False, 96, 96, 0, 2), "death")
    
    def set_mode(self):
        if self.damage:
            self.mode = "damage"
        elif self.attack:
            self.mode = "attack"
        elif self.walk:
            self.mode = "walk"
            self.walk -= 1
            if self.walk == 0:
                self.velocity[0] = 0
        elif self.velocity[0]:
            self.mode = "run"
        elif self.death:
            self.mode = "death"
        else:
            self.mode = "idle"
    
    def update(self):
        super().update()
        self.set_mode()
        if self.walk_cooldown:
            self.walk_cooldown -= 1
        if self.death == 90:
            Coins.add(Coin(*self.rect.center))
            Coins.add(Coin(*self.rect.center))
            Coins.add(Coin(*self.rect.center))

    def wander(self):
        if self.mode != "death" and self.mode != "damage" and self.walk_cooldown == 0:
            self.walk = 30 * random.randint(1, 6)
            self.velocity[0] = random.choice((-1, 1, -2, 2))
            self.walk_cooldown = random.randint(7 * 60, 12 * 60)
    
    def auto_attack(self):
        if self.mode != "attack" and pygame.sprite.collide_rect(King, self) and self.mode != "death":
            self.walk = 0
            self.velocity[0] = 0
            self.dir = 1 if King.x > self.x else 0
            self.attack = sum(self.animation["attack"].steps)

class Golem(AnimatedSprite):
    def __init__(self, x=0, y=0, health=100):
        super().__init__(Animation("src/Golem/idle.png", [10] * 6, 0, True, 160, 160, 0, 2), x, y, health)
        self.walk = 0
        self.damage = 0
        self.imgsize = (60, 88)
        self.walk_cooldown = 0
        self.add_animation(Animation("src/Golem/run.png", [10] * 8, 0, True, 160, 160, 0, 2), "walk")
        self.add_animation(Animation("src/Golem/run.png", [5] * 8, 0, True, 160, 160, 0, 2), "run")
        self.add_animation(Animation("src/Golem/attack.png", [4] * 8, 0, True, 160, 160, 0, 2), "attack")
        self.add_animation(Animation("src/Golem/damage.png", [2, 3, 3, 2], 0, False, 160, 160, 0, 2), "damage")
        self.add_animation(Animation("src/Golem/death.png", [3] * 10, 0, False, 160, 160, 0, 2), "death")
    
    def set_mode(self):
        if self.damage:
            self.mode = "damage"
        elif self.attack:
            self.mode = "attack"
        elif self.walk:
            self.mode = "walk"
            self.walk -= 1
            if self.walk == 0:
                self.velocity[0] = 0
        elif self.velocity[0]:
            self.mode = "run"
        elif self.death:
            self.mode = "death"
        else:
            self.mode = "idle"
    
    def update(self):
        super().update()
        self.set_mode()
        if self.walk_cooldown:
            self.walk_cooldown -= 1
        if self.death == 90:
            for j in' '*10:
                Coins.add(Coin(*self.rect.center))

    def wander(self):
        if self.mode != "death" and self.mode != "damage" and self.walk_cooldown == 0:
            self.walk = 30 * random.randint(1, 6)
            self.velocity[0] = random.choice((-1, 1, -2, 2))
            self.walk_cooldown = random.randint(7 * 60, 12 * 60)
    
    def auto_attack(self):
        if self.mode != "attack" and pygame.sprite.collide_rect(King, self) and self.mode != "death":
            self.walk = 0
            self.velocity[0] = 0
            self.dir = 1 if King.x > self.x else 0
            self.attack = sum(self.animation["attack"].steps)

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

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = pygame.transform.scale(pygame.image.load("src/coin.png").convert_alpha(), (32, 26))
        self.rect = self.img.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.velocity = [random.randint(-5, 5), -1]
        self.death = 0
    
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity[1] += GRAVITY
        self.velocity[0] *= 0.99
        self.rect = self.img.get_rect()
        self.rect.topleft = (self.x, self.y)
        # if collide with Tile_Group then stop
        if pygame.sprite.spritecollide(self, Tile_Group, False):
            self.velocity = [0, 0]
        if pygame.sprite.collide_rect(self, King):
            self.death = -1
            King.coins += 1
        screen.blit(self.img, (self.x, self.y))
        

BLACK = (0, 0, 0)

clock = pygame.time.Clock()
FPS = 60
VELOCITY = 4
JUMPVEL = 8
GRAVITY = 0.5
KING_PADDING = 132
TM_PADDING = 100
G_PADDING = 243
GROUND = SCREEN_SIZE[1] - 128 - KING_PADDING
TILESIZE = 64
King = AnimatedSprite(Animation("src/King/idle.png", [7] * 11, 0, True, 63, 58, 15), 100, GROUND)
King.add_animation(Animation("src/King/run.png", [6] * 8, 0, True, 63, 58, 15), "run")
King.add_animation(Animation("src/King/jump.png", [JUMPVEL//GRAVITY, JUMPVEL//GRAVITY], 0, False, 63, 58), "jump")
King.attack_step = [5, 5, 2]
King.add_animation(Animation("src/King/attack.png", King.attack_step, 0, False, 78, 58, 0), "attack")
King.imgsize = (45, 26)
King.coins = 0

def King_mode(King):
    if King.attack:
        King.mode = "attack"
    elif King.jump:
        King.mode = "jump"
    elif King.velocity[0]:
        King.mode = "run"
    else:
        King.mode = "idle"


Tile_Group = pygame.sprite.Group()
Tile_Group.add(Tile("src/Tile/lefttop.png", 0, GROUND + KING_PADDING))
Tile_Group.add(Tile("src/Tile/leftmiddle.png", 0, GROUND + KING_PADDING + TILESIZE))
for i in range(1, 14):
    Tile_Group.add(Tile("src/Tile/middletop.png", i * TILESIZE, GROUND + KING_PADDING))
    Tile_Group.add(Tile("src/Tile/middlemiddle.png", i * TILESIZE, GROUND + KING_PADDING + TILESIZE))
Tile_Group.add(Tile("src/Tile/righttop.png", (i + 1) * TILESIZE, GROUND + KING_PADDING))
Tile_Group.add(Tile("src/Tile/rightmiddle.png", (i + 1) * TILESIZE, GROUND + KING_PADDING + TILESIZE))

run = True
TMGroup = AnimGroup()
GGroup = AnimGroup()
Coins = AnimGroup()
# TM = TreeMonster(300, GROUND - TM_PADDING)
TMGroup.add(TreeMonster(300, GROUND - TM_PADDING))
TMGroup.add(TreeMonster(500, GROUND - TM_PADDING))
# TMGroup.add(TreeMonster(400, GROUND - TM_PADDING))
GGroup.add(Golem(300, GROUND - G_PADDING))
while run:
    clock.tick(FPS)
    # screen.fill((255, 255, 255))
    screen.blit(pygame.transform.scale(pygame.image.load("src/Tile/BG1.png").convert_alpha(), SCREEN_SIZE), (0, 0))
    screen.blit(pygame.transform.scale(pygame.image.load("src/Tile/BG2.png").convert_alpha(), SCREEN_SIZE), (0, 0))
    screen.blit(pygame.transform.scale(pygame.image.load("src/Tile/BG3.png").convert_alpha(), SCREEN_SIZE), (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                King.velocity[0] += -VELOCITY
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                King.velocity[0] += VELOCITY
            elif event.key in (pygame.K_UP, pygame.K_SPACE) and not King.jump:
                King.velocity[1] += -JUMPVEL
                King.jump = JUMPVEL//GRAVITY*2
            elif event.key == pygame.K_f and not King.attack:
                for TM in TMGroup:
                    if pygame.sprite.collide_rect(King, TM) and TM.mode != "death" and TM.mode != "damage":
                        TM.damage = sum(TM.animation["damage"].steps)
                        TM.health -= 10
                for Gol in GGroup:
                    if pygame.sprite.collide_rect(King, Gol) and Gol.mode != "death" and Gol.mode != "damage":
                        Gol.damage = sum(Gol.animation["damage"].steps)
                        Gol.health -= 10
                King.attack = sum(King.attack_step)
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                King.velocity[0] += VELOCITY
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                King.velocity[0] -= VELOCITY
    King_mode(King)
    TMGroup.update()
    TMGroup.do('wander')
    TMGroup.do('auto_attack')
    GGroup.update()
    GGroup.do('wander')
    GGroup.do('auto_attack')
    King.update()
    Coins.update()
    Tile_Group.draw(screen)
    pygame.display.update()


pygame.quit()
