import pygame
import random
import sys
import os

pygame.init()

# ================= SETTINGS =================
WIDTH, HEIGHT = 1000, 400
FPS = 60
GROUND_Y = 300

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dino")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (120, 0, 200)
BLUE = (40, 40, 90)

# ================= BEST SCORE =================
def load_best():
    if os.path.exists("best.txt"):
        return int(open("best.txt","r").read())
    return 0

def save_best(v):
    with open("best.txt","w") as f:
        f.write(str(v))

# ================= STARS =================
stars = []
for _ in range(120):
    stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)])


# ================= MENU =================
def difficulty_menu():

    menu_font = pygame.font.SysFont("Arial", 60)
    small_font = pygame.font.SysFont("Arial", 32)

    while True:

        for y in range(HEIGHT):
            pygame.draw.line(screen,(10,10,30+y//8),(0,y),(WIDTH,y))

        # stars menu
        for star in stars:
            pygame.draw.circle(screen,WHITE,(int(star[0]),int(star[1])),star[2])
            star[0] -= 0.2
            if star[0] < 0:
                star[0] = WIDTH
                star[1] = random.randint(0, HEIGHT)

        pygame.draw.circle(screen,PURPLE,(820,90),90)
        pygame.draw.rect(screen,(40,40,40),(0,GROUND_Y,WIDTH,HEIGHT))

        title = menu_font.render("SPACE DINO",True,WHITE)
        screen.blit(title,(WIDTH//2-title.get_width()//2,60))

        screen.blit(small_font.render("1 - EASY",True,WHITE),(WIDTH//2-120,200))
        screen.blit(small_font.render("2 - MEDIUM",True,WHITE),(WIDTH//2-120,240))
        screen.blit(small_font.render("3 - UFO MODE",True,WHITE),(WIDTH//2-120,280))
        screen.blit(small_font.render("4 - UFO SAW MODE",True,WHITE),(WIDTH//2-120,320))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    return 5,1
                if e.key == pygame.K_2:
                    return 8,2
                if e.key == pygame.K_3:
                    return 8,3
                if e.key == pygame.K_4:
                    return 8,4


# ================= PLAYER =================
class Player:

    def __init__(self,ufo=False):

        self.rect = pygame.Rect(100,GROUND_Y-52,52,52)
        self.dy = 0
        self.gravity = 0.7
        self.jump_power = -15
        self.jumping = False

        self.ufo_mode = ufo

        self.frames=[]
        for i in range(1,16):
            img = pygame.image.load(f"images/player/run {i}.png")
            img = pygame.transform.scale(img,(60,60))
            self.frames.append(img)

        self.ufo_img = pygame.transform.scale(
            pygame.image.load("images/ufo/ufo.png "),
            (80,80)
        )

        self.frame = 0
        self.timer = 0
        self.has_spear = False

    def jump(self):
        if self.ufo_mode:
            self.dy = -10
        else:
            if not self.jumping:
                self.dy = -15
                self.jumping = True

    def update(self):

        self.dy += self.gravity
        self.rect.y += self.dy

        if self.ufo_mode:
            if self.rect.y < 40:
                self.rect.y = 40
                self.dy = 0
            if self.rect.y > GROUND_Y-52:
                self.rect.y = GROUND_Y-52
                self.dy = 0
        else:
            if self.rect.y >= GROUND_Y-52:
                self.rect.y = GROUND_Y-52
                self.jumping = False

        self.timer += 1
        if self.timer > 5:
            self.frame = (self.frame+1)%len(self.frames)
            self.timer = 0

    def draw(self,s):
        if self.ufo_mode:
            s.blit(self.ufo_img,(self.rect.x,self.rect.y))
        else:
            s.blit(self.frames[self.frame],(self.rect.x-4,self.rect.y-4))


# ================= SPIKE =================
class Spike:
    img = pygame.transform.scale(pygame.image.load("images/spikes/spike.png"),(45,45))

    def __init__(self,x):
        self.rect = pygame.Rect(x+8,GROUND_Y-32,28,32)
        self.scored=False

    def update(self,s): self.rect.x-=s
    def draw(self,s): s.blit(self.img,(self.rect.x-8,self.rect.y-13))


# ================= SAW =================
class Saw:

    def __init__(self):
        self.size = random.choice([60,80,120,160])

        self.img = pygame.transform.scale(
            pygame.image.load("images/saw/saw.png"),
            (self.size,self.size)
        )

        self.rect = pygame.Rect(
            WIDTH+100,
            random.randint(0,GROUND_Y),
            self.size,
            self.size
        )

        self.scored=False

    def update(self,s): self.rect.x-=s
    def draw(self,s): s.blit(self.img,(self.rect.x,self.rect.y))


# ================= SPEAR =================
class Spear:
    img = pygame.transform.scale(pygame.image.load("images/ Spear/spear.png"),(90,90))
    def __init__(self):
        self.rect = pygame.Rect(WIDTH+100,GROUND_Y-90,90,90)
    def update(self,s): self.rect.x-=s
    def draw(self,s): s.blit(self.img,(self.rect.x,self.rect.y))


# ================= GAME =================
class Game:

    def __init__(self,speed,mode):

        self.mode=mode
        self.speed=speed

        self.player=Player(mode==3 or mode==4)

        self.spikes=[]
        self.saws=[]

        self.spear=None
        self.apple=None

        self.score=0
        self.best=load_best()

        self.spawn=0
        self.game_over=False

    def spawn_spikes(self):
        if self.mode!=4:
            x=WIDTH+100
            for i in range(random.choice([1,2])):
                self.spikes.append(Spike(x+i*55))

    def spawn_saw(self):
        if self.mode==4:
            self.saws.append(Saw())

    def update(self):

        if self.game_over: return

        self.player.update()

        # spikes
        if self.mode!=4:
            self.spawn+=1
            if self.spawn>90:
                self.spawn_spikes()
                self.spawn=0

        # saws
        if self.mode==4:
            if random.randint(0,70)==1:
                self.spawn_saw()

        for s in self.spikes[:]:
            s.update(self.speed)

            if not s.scored and s.rect.right < self.player.rect.left:
                s.scored=True
                self.score+=5

            if self.player.rect.colliderect(s.rect):
                self.game_over=True

        for s in self.saws[:]:
            s.update(self.speed)

            if not s.scored and s.rect.right < self.player.rect.left:
                s.scored=True
                self.score+=5

            if self.player.rect.colliderect(s.rect):
                self.game_over=True

        if self.score>self.best:
            self.best=self.score
            save_best(self.best)

    def draw(self):

        # BACKGROUND (НЕ ТРОГАЕМ)
        for y in range(HEIGHT):
            pygame.draw.line(screen,(10,10,30+y//8),(0,y),(WIDTH,y))

        for star in stars:
            pygame.draw.circle(screen,WHITE,(int(star[0]),int(star[1])),star[2])
            star[0]-=self.speed/4
            if star[0]<0:
                star[0]=WIDTH
                star[1]=random.randint(0,HEIGHT)

        pygame.draw.circle(screen,PURPLE,(820,90),90)
        pygame.draw.rect(screen,(40,40,40),(0,GROUND_Y,WIDTH,HEIGHT))

        # OBJECTS
        self.player.draw(screen)

        for s in self.spikes:
            s.draw(screen)

        for s in self.saws:
            s.draw(screen)

        # UI
        font=pygame.font.SysFont("Arial",30)
        screen.blit(font.render(f"Score:{self.score}",True,WHITE),(20,20))
        screen.blit(font.render(f"Best:{self.best}",True,WHITE),(20,50))

        # GAME OVER MENU FIX
        if self.game_over:
            over=pygame.font.SysFont("Arial",60).render("GAME OVER",True,WHITE)
            screen.blit(over,(WIDTH//2-over.get_width()//2,150))
            hint=font.render("R restart | M menu",True,WHITE)
            screen.blit(hint,(WIDTH//2-hint.get_width()//2,220))

        pygame.display.flip()

    def run(self):
        while True:
            clock.tick(FPS)

            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    sys.exit()

                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_SPACE:
                        self.player.jump()

                    if self.game_over:
                        if e.key==pygame.K_r:
                            self.__init__(self.speed,self.mode)
                        if e.key==pygame.K_m:
                            sp,md=difficulty_menu()
                            self.__init__(sp,md)

            self.update()
            self.draw()


# ================= START =================
speed,mode=difficulty_menu()
Game(speed,mode).run()