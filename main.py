import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

# ================= SOUNDS =================
jump_sound = pygame.mixer.Sound("images/sounds/jump/jump-retro-game-jam-fx-1-00-03.mp3")

# easter egg sound (4 seconds)
secret_sound = pygame.mixer.Sound("images/sounds/pashalka/67.mp3")

# ================= SETTINGS =================
WIDTH, HEIGHT = 1000, 400
FPS = 60
GROUND_Y = 300

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dino")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
PURPLE = (120, 0, 200)

# ================= BEST SCORE =================
def load_best():

    if os.path.exists("best.txt"):

        try:
            with open("best.txt", "r") as f:
                return int(f.read())

        except:
            return 0

    return 0

def save_best(v):

    with open("best.txt", "w") as f:
        f.write(str(v))

# ================= STARS =================
stars = []

for _ in range(120):

    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3)
    ])

# ================= MENU =================
def difficulty_menu():

    menu_font = pygame.font.SysFont("Arial", 60)
    small_font = pygame.font.SysFont("Arial", 32)

    while True:

        # background
        for y in range(HEIGHT):

            pygame.draw.line(
                screen,
                (10,10,30+y//8),
                (0,y),
                (WIDTH,y)
            )

        # stars
        for star in stars:

            pygame.draw.circle(
                screen,
                WHITE,
                (int(star[0]), int(star[1])),
                star[2]
            )

            star[0] -= 0.2

            if star[0] < 0:

                star[0] = WIDTH
                star[1] = random.randint(0, HEIGHT)

        pygame.draw.circle(screen, PURPLE, (820,90), 90)

        pygame.draw.rect(
            screen,
            (40,40,40),
            (0,GROUND_Y,WIDTH,HEIGHT)
        )

        title = menu_font.render("SPACE DINO", True, WHITE)

        screen.blit(
            title,
            (WIDTH//2-title.get_width()//2,60)
        )

        screen.blit(
            small_font.render("1 - EASY", True, WHITE),
            (WIDTH//2-120,200)
        )

        screen.blit(
            small_font.render("2 - MEDIUM", True, WHITE),
            (WIDTH//2-120,240)
        )

        screen.blit(
            small_font.render("3 - HARD", True, WHITE),
            (WIDTH//2-120,280)
        )

        screen.blit(
            small_font.render("4 - UFO SAW MODE", True, WHITE),
            (WIDTH//2-120,320)
        )

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
                    return 16,3

                if e.key == pygame.K_4:
                    return 8,4


# ================= PLAYER =================
class Player:

    def __init__(self, ufo=False):

        self.rect = pygame.Rect(
            100,
            GROUND_Y-52,
            52,
            52
        )

        self.dy = 0
        self.gravity = 0.7
        self.jumping = False

        self.ufo_mode = ufo

        self.frames = []

        for i in range(1,16):

            img = pygame.image.load(
                f"images/player/run {i}.png"
            )

            img = pygame.transform.scale(
                img,
                (60,60)
            )

            self.frames.append(img)

        self.ufo_img = pygame.transform.scale(
            pygame.image.load("images/ufo/ufo.png"),
            (80,80)
        )

        self.frame = 0
        self.timer = 0

    def jump(self):

        jump_sound.play()

        if self.ufo_mode:

            self.dy = -10

        else:

            if not self.jumping:

                self.dy = -15
                self.jumping = True

    def update(self):

        self.dy += self.gravity
        self.rect.y += self.dy

        # UFO
        if self.ufo_mode:

            if self.rect.y < 40:

                self.rect.y = 40
                self.dy = 0

            if self.rect.y > GROUND_Y-52:

                self.rect.y = GROUND_Y-52
                self.dy = 0

        # NORMAL
        else:

            if self.rect.y >= GROUND_Y-52:

                self.rect.y = GROUND_Y-52
                self.jumping = False

        # animation
        self.timer += 1

        if self.timer > 5:

            self.frame = (self.frame+1) % len(self.frames)
            self.timer = 0

    def draw(self, s):

        if self.ufo_mode:

            s.blit(
                self.ufo_img,
                (self.rect.x,self.rect.y)
            )

        else:

            s.blit(
                self.frames[self.frame],
                (self.rect.x-4,self.rect.y-4)
            )


# ================= SPIKE =================
class Spike:

    img = pygame.transform.scale(
        pygame.image.load("images/spikes/spike.png"),
        (45,45)
    )

    def __init__(self, x):

        self.rect = pygame.Rect(
            x+8,
            GROUND_Y-32,
            28,
            32
        )

        self.scored = False

    def update(self, speed):

        self.rect.x -= speed

    def draw(self, s):

        s.blit(
            self.img,
            (self.rect.x-8,self.rect.y-13)
        )


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

        self.scored = False

    def update(self, speed):

        self.rect.x -= speed

    def draw(self, s):

        s.blit(
            self.img,
            (self.rect.x,self.rect.y)
        )


# ================= GAME =================
class Game:

    def __init__(self, speed, mode):

        self.mode = mode
        self.speed = speed

        self.player = Player(mode == 4)

        self.spikes = []
        self.saws = []

        self.score = 0
        self.best = load_best()

        self.spawn = 0
        self.game_over = False

        # ================= EASTER EGG =================
        self.secret_used = False
        self.secret_active = False
        self.secret_start = 0

    def spawn_spikes(self):

        if self.mode != 4:

            x = WIDTH+100

            for i in range(random.choice([1,2])):

                self.spikes.append(
                    Spike(x+i*55)
                )

    def spawn_saw(self):

        if self.mode == 4:

            self.saws.append(Saw())

    def update(self):

        # freeze game during easter egg
        if self.secret_active:

            now = pygame.time.get_ticks()

            # 4 seconds
            if now - self.secret_start >= 4000:

                self.secret_active = False

            return

        if self.game_over:
            return

        self.player.update()

        # spikes
        if self.mode != 4:

            self.spawn += 1

            if self.spawn > 90:

                self.spawn_spikes()
                self.spawn = 0

        # saws
        if self.mode == 4:

            if random.randint(0,70) == 1:

                self.spawn_saw()

        # spikes update
        for s in self.spikes[:]:

            s.update(self.speed)

            if not s.scored and \
               s.rect.right < self.player.rect.left:

                s.scored = True
                self.score += 5

            if self.player.rect.colliderect(s.rect):

                self.game_over = True

            if s.rect.right < 0:

                self.spikes.remove(s)

        # saws update
        for s in self.saws[:]:

            s.update(self.speed)

            if not s.scored and \
               s.rect.right < self.player.rect.left:

                s.scored = True
                self.score += 5

            if self.player.rect.colliderect(s.rect):

                self.game_over = True

            if s.rect.right < 0:

                self.saws.remove(s)

        # ================= SECRET 67 EVENT =================
        if self.mode == 3 and not self.secret_used:

            # 50% chance
            if self.score >= 50 and random.randint(1,2) == 1:

                self.score = 67

                secret_sound.play()

                self.secret_active = True
                self.secret_start = pygame.time.get_ticks()

                self.secret_used = True

        # save best
        if self.score > self.best:

            self.best = self.score
            save_best(self.best)

    def draw(self):

        # background
        for y in range(HEIGHT):

            pygame.draw.line(
                screen,
                (10,10,30+y//8),
                (0,y),
                (WIDTH,y)
            )

        # stars
        for star in stars:

            pygame.draw.circle(
                screen,
                WHITE,
                (int(star[0]),int(star[1])),
                star[2]
            )

            if not self.secret_active:
                star[0] -= self.speed / 4

            if star[0] < 0:

                star[0] = WIDTH
                star[1] = random.randint(0, HEIGHT)

        pygame.draw.circle(screen, PURPLE, (820,90), 90)

        pygame.draw.rect(
            screen,
            (40,40,40),
            (0,GROUND_Y,WIDTH,HEIGHT)
        )

        # player
        self.player.draw(screen)

        # spikes
        for s in self.spikes:
            s.draw(screen)

        # saws
        for s in self.saws:
            s.draw(screen)

        # UI
        font = pygame.font.SysFont("Arial",30)

        screen.blit(
            font.render(f"Score: {self.score}", True, WHITE),
            (20,20)
        )

        screen.blit(
            font.render(f"Best: {self.best}", True, WHITE),
            (20,50)
        )

        # secret text
        if self.secret_active:

            secret_font = pygame.font.SysFont("Arial", 70)

            txt = secret_font.render(
                "SECRET 67",
                True,
                (255,0,0)
            )

            screen.blit(
                txt,
                (WIDTH//2-txt.get_width()//2,120)
            )

        # game over
        if self.game_over:

            over = pygame.font.SysFont(
                "Arial",
                60
            ).render("GAME OVER", True, WHITE)

            screen.blit(
                over,
                (WIDTH//2-over.get_width()//2,150)
            )

            hint = font.render(
                "R restart | M menu",
                True,
                WHITE
            )

            screen.blit(
                hint,
                (WIDTH//2-hint.get_width()//2,220)
            )

        pygame.display.flip()

    def run(self):

        while True:

            clock.tick(FPS)

            for e in pygame.event.get():

                if e.type == pygame.QUIT:

                    sys.exit()

                if e.type == pygame.KEYDOWN:

                    if e.key == pygame.K_SPACE:

                        self.player.jump()

                    if self.game_over:

                        if e.key == pygame.K_r:

                            self.__init__(
                                self.speed,
                                self.mode
                            )

                        if e.key == pygame.K_m:

                            sp, md = difficulty_menu()

                            self.__init__(sp, md)

            self.update()
            self.draw()


# ================= START =================
speed, mode = difficulty_menu()
Game(speed, mode).run()