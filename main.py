import pygame
import random
from Animation import Animation, AnimGroup, Tile, TILESIZE, Button
pygame.init()

# SCREEN_SIZE = (960, 576)
SCREEN_SIZE = (1200, 720)

font = pygame.font.Font("./src/neodgm.ttf", 40)
smallfont = pygame.font.Font("./src/neodgm.ttf", 25)

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Nordic Journey")

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
        self.enter = 0
        self.dash = 0
        self.kp = 0
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
        self.rect = pygame.Rect(self.x + self.image.get_width()  / 2 - self.imgsize[0] * 1.6,
                                self.y + self.image.get_height() / 2 - self.imgsize[1] * 1.6,
                                self.imgsize[0] * 3.1,
                                self.imgsize[1] * 3)
        for i in Tile_Group:
            if pygame.sprite.collide_rect(self, i):
                self.x -= self.velocity[0]
                break
        
        self.y += self.velocity[1]
        self.rect = pygame.Rect(self.x + self.image.get_width()  / 2 - self.imgsize[0] * 1.6,
                                self.y + self.image.get_height() / 2 - self.imgsize[1] * 1.6,
                                self.imgsize[0] * 3.1,
                                self.imgsize[1] * 3)
        for i in Tile_Group:
            if pygame.sprite.collide_rect(self, i):
                self.y -= self.velocity[1]
                self.velocity[1] = 0
                break
        
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
        # if self.y > GROUND:
        #     self.y = GROUND
        #     self.velocity[1] = 0
        #     self.jump = 0
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
        if self.enter > 0:
            self.enter -= 1
        if self.kp == 0:
            self.velocity[0] = 0
            self.dash = 0

        if self.dash > 0:
            self.dash -= 1
            if self.dash in (20, 15, 12, 10):
                self.velocity[0] -= (DASH_SPEED if King.dir else -DASH_SPEED)
        self.rect = pygame.Rect(self.x + self.image.get_width()  / 2 - self.imgsize[0] * 1.6,
                                self.y + self.image.get_height() / 2 - self.imgsize[1] * 1.6,
                                self.imgsize[0] * 3.1,
                                self.imgsize[1] * 3)
        # print(self.x - self.imgsize[0] / 2, self.y - self.imgsize[1] / 2, self.imgsize[0], self.imgsize[1])
        self.image = self.animation[self.mode].image if self.dir else pygame.transform.flip(self.animation[self.mode].image.convert_alpha(), True, False)
        screen.blit(self.image, (self.x, self.y))
        # pygame.draw.rect(screen, (0, 255, 0), self.rect)

    def add_animation(self, animation, mode):
        self.animation[mode] = animation
        self.modes.append(mode)

class Mob(AnimatedSprite):
    def __init__(self, idle_animation, x=0, y=0, health=1):
        super().__init__(idle_animation, x, y, health)
        self.knockback = 10
        self.walk = 0
        self.damage = 0
        self.walk_cooldown = 0
        self.attack_cooldown = 0
        self.kp = 1

    def set_mode(self):
        if self.damage:
            self.mode = "damage"
        elif self.attack > self.attack_cooldown:
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
        if self.damage == 1:
            self.x -= (1 if King.rect.centerx > self.rect.centerx else -1) * self.knockback
        if self.rect.right > SCREEN_SIZE[0]:
            self.x -= self.rect.right - SCREEN_SIZE[0]

    def wander(self):
        if self.mode not in ["damage", "death", "attack"] and self.walk_cooldown == 0:
            self.walk = 30 * random.randint(1, 6)
            self.velocity[0] = random.choice((-1, 1, -2, 2))
            self.walk_cooldown = random.randint(5 * 60, 10 * 60)
    
    def auto_attack(self):
        if self.mode not in ["attack", "death"] and pygame.sprite.collide_rect(King, self) and self.attack == 0:
            self.walk = 0
            self.velocity[0] = 0
            self.dir = 1 if King.rect.centerx > self.rect.centerx else 0
            self.attack = sum(self.animation["attack"].steps) + self.attack_cooldown
    
    def chase(self):
        if self.mode not in ["damage", "death", "attack"] and self.walk_cooldown == 0:
            self.walk = 30 * random.randint(1, 6)
            self.velocity[0] = 2 * (1 if King.rect.centerx > self.rect.centerx else -1)
            self.walk_cooldown = random.randint(5 * 60, 10 * 60)

class TreeMonster(Mob):
    def __init__(self, x=0, y=0, health=40):
        super().__init__(Animation("./src/TreeMonster/idle.png", [15] * 4, 0, True, 96, 96, 0, 2), x, y, health)
        self.imgsize = (49, 61)
        self.add_animation(Animation("./src/TreeMonster/run.png", [10] * 5, 0, True, 96, 96, 0, 2), "walk")
        self.add_animation(Animation("./src/TreeMonster/run.png", [5] * 5, 0, True, 96, 96, 0, 2), "run")
        self.add_animation(Animation("./src/TreeMonster/attack.png", [4] * 6, 0, True, 96, 96, 0, 2), "attack")
        self.add_animation(Animation("./src/TreeMonster/damage.png", [2, 2, 3, 3, 3], 0, False, 96, 96, 0, 2), "damage")
        self.add_animation(Animation("./src/TreeMonster/death.png", [5] * 8, 0, False, 96, 96, 0, 2), "death")
    
    def update(self):
        super().update()
        self.set_mode()
        if self.walk_cooldown:
            self.walk_cooldown -= 1
        if self.death == 90:
            for i in range(random.randint(2, 4)):
                Coins.add(Coin(*self.rect.center))

class Golem(Mob):
    def __init__(self, x=0, y=0, health=100):
        super().__init__(Animation("./src/Golem/idle.png", [10] * 6, 0, True, 160, 160, 0, 2), x, y, health)
        self.imgsize = (60, 88)
        self.attack_cooldown = 120
        self.add_animation(Animation("./src/Golem/run.png", [12] * 8, 0, True, 160, 160, 0, 2), "walk")
        self.add_animation(Animation("./src/Golem/run.png", [8] * 8, 0, True, 160, 160, 0, 2), "run")
        self.add_animation(Animation("./src/Golem/attack.png", [5] * 8, 0, True, 160, 160, 0, 2), "attack")
        self.add_animation(Animation("./src/Golem/damage.png", [2, 3, 3, 2], 0, False, 160, 160, 0, 2), "damage")
        self.add_animation(Animation("./src/Golem/death.png", [5] * 10, 0, False, 160, 160, 0, 2), "death")

    def update(self):
        super().update()
        self.set_mode()
        if self.walk_cooldown:
            self.walk_cooldown -= 1
        if self.mode == "damage": self.attack = self.attack_cooldown
        if self.death == 90:
            for j in' '*random.randint(23, 27):
                Coins.add(Coin(*self.rect.center))

class Boss(Mob):
    def __init__(self, x=0, y=0, health=500):
        super().__init__(Animation('./src/Boss/idle.png', [10] * 6, 0, True, 192, 128, 0, 3), x, y, health)
        self.imgsize = (192, 128)
        self.add_animation(Animation('./src/Boss/run.png', [10] * 10, 0, True, 192, 128, 0, 3), 'walk')
        self.add_animation(Animation('./src/Boss/run.png', [5] * 10, 0, True, 192, 128, 0, 3), 'run')
        self.add_animation(Animation('./src/Boss/attack.png', [6] * 14, 0, True, 192, 128, 0, 3), 'attack')
        self.add_animation(Animation('./src/Boss/damage.png', [3] * 7, 0, False, 192, 128, 0, 3), 'damage')
        self.add_animation(Animation('./src/Boss/death.png', [3] * 16, 0, False, 192, 128, 0, 3), 'death')
    
    def update(self):
        global CLEAR
        global FPS
        for mode in self.modes:
            if mode != self.mode:
                self.animation[mode].reset()
        self.x += self.velocity[0]
        self.rect = pygame.Rect(self.x + self.image.get_width()  / 2 - self.imgsize[0] * 1.6,
                                self.y + self.image.get_height() / 2 - self.imgsize[1] * 1.6,
                                self.imgsize[0] * 3.1,
                                self.imgsize[1] * 3)
        for i in Tile_Group:
            if pygame.sprite.collide_rect(self, i):
                self.x -= self.velocity[0]
                break
        
        self.y += self.velocity[1]
        self.rect = pygame.Rect(self.x + self.image.get_width()  / 2 - self.imgsize[0] * 1.6,
                                self.y + self.image.get_height() / 2 - self.imgsize[1] * 1.6,
                                self.imgsize[0] * 3.1,
                                self.imgsize[1] * 3)
        for i in Tile_Group:
            if pygame.sprite.collide_rect(self, i):
                self.y -= self.velocity[1]
                self.velocity[1] = 0
                break
        
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
        # if self.y > GROUND:
        #     self.y = GROUND
        #     self.velocity[1] = 0
        #     self.jump = 0
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
        if self.enter > 0:
            self.enter -= 1
        if self.kp == 0:
            self.velocity[0] = 0
            self.dash = 0

        if self.dash > 0:
            self.dash -= 1
            if self.dash in (20, 15, 12, 10):
                self.velocity[0] -= (DASH_SPEED if King.dir else -DASH_SPEED)
        self.rect = pygame.Rect(self.x + self.image.get_width()  / 2 - self.imgsize[0] * 1.6,
                                self.y + self.image.get_height() / 2 - self.imgsize[1] * 1.6,
                                self.imgsize[0] * 3.1,
                                self.imgsize[1] * 3)
        # print(self.x - self.imgsize[0] / 2, self.y - self.imgsize[1] / 2, self.imgsize[0], self.imgsize[1])
        self.image = self.animation[self.mode].image if self.dir else pygame.transform.flip(self.animation[self.mode].image.convert_alpha(), True, False)
        screen.blit(self.image, (self.x, self.y))
        # pygame.draw.rect(screen, (0, 255, 0), self.rect)
        self.set_mode()
        if self.death > 40 and self.mode == "death": FPS = 10
        else: FPS = 60
        if self.walk_cooldown:
            self.walk_cooldown -= 1
        if self.mode == "damage":
            self.attack = 0
            self.walk = 0
        if self.death == 90:
            for j in' '*100:
                Coins.add(Coin(*self.rect.center))
            CLEAR = True

class Effect(AnimatedSprite):
    def __init__(self, animation, x, y):
        super().__init__(animation, x, y)
        self.add_animation(animation, "death")
        self.mode = "death"
        self.death = sum(self.animation["death"].steps)

    def update(self):
        self.animation[self.mode].update()
        self.death -= 1
        if self.death == 0: return
        self.rect = pygame.Rect(self.x + self.image.get_width()  / 2 - self.imgsize[0] * 1.6,
                                self.y + self.image.get_height() / 2 - self.imgsize[1] * 1.6,
                                self.imgsize[0] * 3.2,
                                self.imgsize[1] * 3.2)
        # print(self.x - self.imgsize[0] / 2, self.y - self.imgsize[1] / 2, self.imgsize[0], self.imgsize[1])
        self.image = self.animation[self.mode].image if King.dir else pygame.transform.flip(self.animation[self.mode].image.convert_alpha(), True, False)
        # print(self.animation[self.mode].step_idx, self.animation[self.mode].current_frame)
        screen.blit(self.image, (self.x, self.y))

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = pygame.transform.scale(pygame.image.load("./src/coin.png").convert_alpha(), (32, 26))
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
        if pygame.sprite.spritecollide(self, Tile_Group, False):
            self.velocity = [0, 0]
        if pygame.sprite.collide_rect(self, King):
            self.death = -1
            King.coins += 1
        if self.rect.right > SCREEN_SIZE[0]:
            self.x -= self.rect.right - SCREEN_SIZE[0]
        screen.blit(self.img, (self.x, self.y))

class Door(AnimatedSprite):
    def __init__(self, x, y):
        super().__init__(Animation("./src/Door/idle.png", [1], 0, True, 46, 56), x, y)
        self.imgsize = (46, 56)
        self.add_animation(Animation("./src/Door/open.png", [10] * 5, 0, True, 46, 56), "open")
        self.add_animation(Animation("./src/Door/close.png", [10] * 3, 0, True, 46, 56), "close")
        self.mode = "idle"
        self.open = 0
        self.close = 0

    def update(self):
        for mode in self.modes:
            if mode != self.mode:
                self.animation[mode].reset()
        self.animation[self.mode].update()
        if self.open:
            self.mode = "open"
            self.open -= 1
            if self.open == 0:
                self.mode = "close"
                self.close = sum(self.animation["close"].steps)
        elif self.close:
            self.close -= 1
            if self.close == 0:
                self.mode = "idle"
            
        self.rect = pygame.Rect(self.x + self.image.get_width()  / 2 - self.imgsize[0] * 1.6,
                                self.y + self.image.get_height() / 2 - self.imgsize[1] * 1.6,
                                self.imgsize[0] * 3.2,
                                self.imgsize[1] * 3.2)
        self.image = self.animation[self.mode].image
        screen.blit(self.image, (self.x, self.y))
        # pygame.draw.rect(screen, (0, 255, 0), self.rect)

clock = pygame.time.Clock()
FPS = 60
VELOCITY = 4
DASH_SPEED = 0
JUMPVEL = 8
GRAVITY = 0.5
KING_PADDING = 132
TM_PADDING = 102
G_PADDING = 243
DAMAGE = 6
GROUND = SCREEN_SIZE[1] - 128 - KING_PADDING
HEALTHUP_PRICE = 20
SPEEDUP_PRICE = 40
DAMAGEUP_PRICE = 30
CLEAR = False
RETURNHOME = 0
Doors = AnimGroup()
Dooridx = -1
King = AnimatedSprite(Animation("./src/King/idle.png", [7] * 11, 0, True, 63, 58, 15), 10, GROUND)
King.add_animation(Animation("./src/King/run.png", [6] * 8, 0, True, 63, 58, 15), "run")
King.add_animation(Animation("./src/King/jump.png", [JUMPVEL//GRAVITY, JUMPVEL//GRAVITY], 0, False, 63, 58), "jump")
King.add_animation(Animation("./src/King/attack.png", [5, 5, 2], 0, False, 78, 58, 0), "attack")
King.add_animation(Animation("./src/King/damage.png", [6] * 2, 0, True, 63, 58, 15), "damage")
King.add_animation(Animation("./src/King/enter.png", [6] * 8 + [30 + 30], 0, False, 63, 58, 15), "enter")
King.add_animation(Animation("./src/King/exit.png", [6] * 8, 0, False, 63, 58, 15), "exit")
King.add_animation(Animation("./src/King/death.png", [6] * 4, 0, False, 63, 58, 15), "death")
King.imgsize = (45, 26)
King.coins = 0
King.dash = 0
King.hitbyboss = 0

def King_mode(King):
    global RETURNHOME
    if King.health <= 0:
        King.mode = "death"
        if RETURNHOME == 0:
            RETURNHOME = 180
        return
    if King.y > GROUND:
        King.y = GROUND
    for mob in GGroup:
        if mob.mode == 'attack' and mob.animation['attack'].step_idx == 5 and mob.animation['attack'].current_frame == 1:
            King.health -= 20
            King.damage = 2 * sum(King.animation["damage"].steps)
    for mob in TMGroup:
        if mob.mode == 'attack' and mob.animation['attack'].step_idx == 3 and mob.animation['attack'].current_frame == 1:
            King.health -= 5
            King.damage = 2 * sum(King.animation["damage"].steps)
    for boss in BGroup:
        if boss.mode == 'attack' and boss.animation['attack'].step_idx == 7 and boss.animation['attack'].current_frame == 1:
            King.health -= 50
            King.damage = 3 * sum(King.animation["damage"].steps)
            King.hitbyboss = 50 * (1 if King.rect.centerx > mob.rect.centerx else -1)
    if King.damage:
        King.mode = "damage"
        if King.hitbyboss:
            King.x += King.hitbyboss
            King.hitbyboss -= 5 * (1 if King.hitbyboss > 0 else -1)
    elif King.attack:
        King.mode = "attack"
    elif King.enter:
        King.mode = "enter"
        King.velocity[0] = 0
        King.dash = 0
        if King.enter == 1:
            stagechange()
    elif King.jump:
        King.mode = "jump"
    elif King.velocity[0]:
        King.mode = "run"
    else:
        King.mode = "idle"

def stagechange():
    global menuidx
    global Doors
    global Dooridx
    if Dooridx == 1:
        menuidx = 1
        Doors = AnimGroup()
        Doors.add(Door(1000, GROUND - 34))
        if Stage_no == 0:
            TMGroup.add(TreeMonster(300, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(400, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(500, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(600, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(700, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(800, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(900, GROUND - TM_PADDING))
        elif Stage_no == 1:
            TMGroup.add(TreeMonster(300, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(400, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(500, GROUND - TM_PADDING))
            GGroup.add(Golem(600, GROUND - G_PADDING))
            GGroup.add(Golem(1000, GROUND - G_PADDING))
            TMGroup.add(TreeMonster(800, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(900, GROUND - TM_PADDING))
        elif Stage_no == 2:
            BGroup.add(Boss(600, GROUND - 198))
            TMGroup.add(TreeMonster(250, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(400, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(700, GROUND - TM_PADDING))
            TMGroup.add(TreeMonster(800, GROUND - TM_PADDING))
            GGroup.add(Golem(450, GROUND - G_PADDING))
            GGroup.add(Golem(900, GROUND - G_PADDING))
            
    elif Dooridx == -1:
        menuidx = 0
        Doors = AnimGroup()
        Doors.add(Door(600, GROUND - 34))
        Doors.add(Door(800, GROUND - 34))
        Doors.add(Door(1000, GROUND - 34))
    King.x, King.y = 10, GROUND
    Dooridx = -1

Shop = Tile("./src/Shop/Shop.png", 350, 530, 28 * 4, 16 * 4)
Tile_Group = pygame.sprite.Group()
Tile_Group.add(Tile("./src/coin.png", 16, 16, 16 * 3, 13 * 3))
Tile_Group.add(Tile("./src/heart.png", 18, 64, 11 * 4, 11 * 4))
Tile_Group.add(Tile("./src/Tile/lefttop.png", 0, GROUND + KING_PADDING))
Tile_Group.add(Tile("./src/Tile/leftmiddle.png", 0, GROUND + KING_PADDING + TILESIZE))
for i in range(1, 18):
    Tile_Group.add(Tile("./src/Tile/middletop.png", i * TILESIZE, GROUND + KING_PADDING))
    Tile_Group.add(Tile("./src/Tile/middlemiddle.png", i * TILESIZE, GROUND + KING_PADDING + TILESIZE))
Tile_Group.add(Tile("./src/Tile/righttop.png", (i + 1) * TILESIZE, GROUND + KING_PADDING))
Tile_Group.add(Tile("./src/Tile/rightmiddle.png", (i + 1) * TILESIZE, GROUND + KING_PADDING + TILESIZE))

run = True
TMGroup = AnimGroup()
GGroup = AnimGroup()
Coins = AnimGroup()
Effects = AnimGroup()
BGroup = AnimGroup()
Speedupgrade = Button("./src/Shop/speed.png", SCREEN_SIZE[0] // 2 - 64, 128, 128, 128)
Healthupgrade = Button("./src/Shop/health.png", SCREEN_SIZE[0] // 2 - 64 * 5, 128, 128, 128)
Damageupgrade = Button("./src/Shop/strength.png", SCREEN_SIZE[0] // 2 + 64 * 3, 128, 128, 128)
# Effects.add(Effect(Animation("./src/Effects/dash.png", [10] * 5, 0, False, 48, 32), 300, GROUND - TM_PADDING))
# GGroup.add(Golem(300, GROUND - G_PADDING))
MENU = ['main', 'stage', 'boss', 'shop']
menuidx = 0
stagechange()
STAGE_1_CLEAR = False
Stage_no = 0
while run:
    clock.tick(FPS)
    # screen.fill((255, 255, 255))
    screen.blit(pygame.transform.scale(pygame.image.load("./src/Tile/BG1.png").convert_alpha(), SCREEN_SIZE), (0, 0))
    screen.blit(pygame.transform.scale(pygame.image.load("./src/Tile/BG2.png").convert_alpha(), SCREEN_SIZE), (0, 0))
    screen.blit(pygame.transform.scale(pygame.image.load("./src/Tile/BG3.png").convert_alpha(), SCREEN_SIZE), (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and King.mode not in ['enter', 'exit'] and RETURNHOME == 0:
            if event.key == pygame.K_m and MENU[menuidx] == 'shop':
                King.coins += 10000
            elif event.key == pygame.K_d and King.dash == 0 and King.velocity[0] and DASH_SPEED:
                Effects.add(Effect(Animation("./src/Effects/dash1.png", [3] * 7, 0, False, 64, 32), King.x, (King.y + King.rect.centery) // 2 + 1))
                Effects.add(Effect(Animation("./src/Effects/Smoke/dash.png", [2] * 10, 0, False, 43, 53), King.x, (King.y + King.rect.centery) // 2 - 70))
                # King.velocity[0] *= 5
                King.velocity[0] += 4 * DASH_SPEED * ((King.velocity[0] > 0) - (King.velocity[0] < 0))
                King.dash = 30
            elif event.key in (pygame.K_LEFT,):
                King.kp = 1
                King.velocity[0] += -VELOCITY
            elif event.key in (pygame.K_RIGHT,):
                King.kp = 1
                King.velocity[0] += VELOCITY
            elif event.key in (pygame.K_UP, pygame.K_SPACE) and not King.jump:
                King.velocity[1] += -JUMPVEL
                King.jump = JUMPVEL//GRAVITY*2
            elif event.key == pygame.K_z and not King.attack:
                for idx in range(len(Doors)):
                    d = Doors[idx]
                    if pygame.sprite.collide_rect(King, d) and d.mode == "idle":
                        d.mode = "open"
                        d.open = sum(d.animation["open"].steps)
                        King.mode = "enter"
                        King.enter = sum(King.animation["enter"].steps)
                        King.x = d.x - (30 if King.dir else 20)
                        if MENU[menuidx] == 'main' or MENU[menuidx] == 'shop':
                            Dooridx = 1
                            Stage_no = idx
                        if MENU[menuidx] == 'stage':
                            Dooridx = -1
                            for __ in range(10): Coins.add(Coin(d.rect.centerx, d.rect.top))
                            King.health += 10
                        break
                if MENU[menuidx] == 'stage':
                    for TM in TMGroup:
                        if pygame.sprite.collide_rect(King, TM) and TM.mode != "death" and TM.mode != "damage":
                            TM.damage = sum(TM.animation["damage"].steps)
                            TM.health -= DAMAGE
                    for Gol in GGroup:
                        if pygame.sprite.collide_rect(King, Gol) and Gol.mode != "death" and Gol.mode != "damage":
                            Gol.damage = sum(Gol.animation["damage"].steps)
                            Gol.health -= DAMAGE
                    for Bos in BGroup:
                        if pygame.sprite.collide_rect(King, Bos) and Bos.mode != "death" and Bos.mode != "damage":
                            Bos.damage = sum(Bos.animation["damage"].steps)
                            Bos.health -= DAMAGE
                    King.attack = sum(King.animation["attack"].steps)
                elif MENU[menuidx] == 'main':
                    if pygame.sprite.collide_rect(King, Shop):
                        menuidx = 3
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                King.kp = 0
    Tile_Group.draw(screen)
    screen.blit(font.render(f"{King.coins}", True, (255, 255, 255)), (74, 18))
    screen.blit(font.render(f"{King.health}", True, (255, 255, 255)), (72, 66))
    if MENU[menuidx] == 'shop':
        Healthupgrade.draw(screen)
        Speedupgrade. draw(screen)
        Damageupgrade.draw(screen)
        Doors.update()
        screen.blit(Shop.image, Shop.rect.topleft)
        screen.blit(pygame.transform.scale(pygame.image.load("./src/coin.png").convert_alpha(), (16 * 2, 13 * 2)), (SCREEN_SIZE[0] // 2 - 64 * 5, 256))
        screen.blit(pygame.transform.scale(pygame.image.load("./src/coin.png").convert_alpha(), (16 * 2, 13 * 2)), (SCREEN_SIZE[0] // 2 - 64 * 1, 256))
        screen.blit(pygame.transform.scale(pygame.image.load("./src/coin.png").convert_alpha(), (16 * 2, 13 * 2)), (SCREEN_SIZE[0] // 2 + 64 * 3, 256))
        screen.blit(smallfont.render(f"{HEALTHUP_PRICE}", True, (255, 255, 255)), (SCREEN_SIZE[0] // 2 - 64 * 5 + 37, 258))
        screen.blit(smallfont.render(f"{SPEEDUP_PRICE}", True, (255, 255, 255)), (SCREEN_SIZE[0] // 2 - 64 * 1 + 37, 258))
        screen.blit(smallfont.render(f"{DAMAGEUP_PRICE}", True, (255, 255, 255)), (SCREEN_SIZE[0] // 2 + 64 * 3 + 37, 258))
        if Speedupgrade.clicked:
            if King.coins >= SPEEDUP_PRICE:
                King.coins -= SPEEDUP_PRICE
                SPEEDUP_PRICE += 20
                DASH_SPEED += 1
            Speedupgrade.clicked = False
        if Healthupgrade.clicked:
            if King.coins >= HEALTHUP_PRICE:
                King.coins -= HEALTHUP_PRICE
                HEALTHUP_PRICE += 10
                King.health += 15
            Healthupgrade.clicked = False
        if Damageupgrade.clicked:
            if King.coins >= DAMAGEUP_PRICE:
                King.coins -= DAMAGEUP_PRICE
                DAMAGE += 1
                DAMAGEUP_PRICE += 20
            Damageupgrade.clicked = False
    if MENU[menuidx] == 'stage':
        TMGroup.update()
        GGroup.update()
        if not TMGroup and not GGroup and not BGroup:
            Doors.update()
        if Stage_no == 2:
            BGroup.update()
            BGroup.do('auto_attack')
            if not BGroup or BGroup[0].health < 500:
                BGroup.do('chase')
                TMGroup.do('chase')
                GGroup.do('chase')
                BGroup.do('auto_attack')
            else:
                for t in TMGroup: t.dir = 0
                for g in GGroup: g.dir = 0
                if BGroup: BGroup[0].dir = 0
        else:
            TMGroup.do('wander')
            GGroup.do('wander')
        TMGroup.do('auto_attack')
        GGroup.do('auto_attack')
        if RETURNHOME > 0:
            RETURNHOME -= 1

        if RETURNHOME == 1:
            RETURNHOME = 0
            Dooridx = -1
            King.health = 100
            DASH_SPEED = 0
            King.coins = 0
            TMGroup = AnimGroup()
            GGroup = AnimGroup()
            Coins = AnimGroup()
            BGroup = AnimGroup()
            stagechange()

    Coins.update()
    if MENU[menuidx] == 'main':
        Doors.update()
        screen.blit(Shop.image, Shop.rect.topleft)
    King_mode(King)
    King.update()
    Effects.update()
    pygame.display.update()


pygame.quit()
