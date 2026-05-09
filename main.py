import pygame
import random
import sys

pygame.init()

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

stars = []
for _ in range(120):
    stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)])


class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, GROUND_Y - 52, 52, 52)

        self.dy = 0
        self.gravity = 0.7
        self.jump_power = -15
        self.jumping = False

        self.frames = []
        for i in range(1, 16):
            img = pygame.image.load(f"images/player/run {i}.png")
            img = pygame.transform.scale(img, (60, 60))
            self.frames.append(img)

        self.frame = 0
        self.timer = 0

        self.has_spear = False

    def jump(self):
        if not self.jumping:
            self.dy = self.jump_power
            self.jumping = True

    def update(self):
        self.dy += self.gravity
        self.rect.y += self.dy

        if self.rect.y >= GROUND_Y - 52:
            self.rect.y = GROUND_Y - 52
            self.jumping = False

        self.timer += 1
        if self.timer >= 5:
            self.frame = (self.frame + 1) % len(self.frames)
            self.timer = 0

    def draw(self, surface):
        surface.blit(self.frames[self.frame], (self.rect.x - 4, self.rect.y - 4))


class Spike:
    image = pygame.transform.scale(pygame.image.load("images/spikes/spike.png"), (45, 45))

    def __init__(self, x):
        self.rect = pygame.Rect(x + 8, GROUND_Y - 32, 28, 32)
        self.scored = False

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x - 8, self.rect.y - 13))


class Spear:
    image = pygame.transform.scale(pygame.image.load("images/ Spear/spear.png"), (90, 90))

    def __init__(self):
        self.rect = pygame.Rect(WIDTH + 100, GROUND_Y - 90, 90, 90)
        self.active = True

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))


class Game:
    def __init__(self):
        self.player = Player()
        self.spikes = []

        self.spear = None
        self.spear_taken = False

        self.score = 0
        self.speed = 7

        self.font = pygame.font.SysFont("Arial", 32)
        self.big_font = pygame.font.SysFont("Arial", 60)

        self.spawn_timer = 0
        self.next_spawn = random.randint(70, 120)

        self.game_over = False
        self.win = False

    def spawn_spikes(self):
        count = random.choice([1, 1, 2])
        x = WIDTH + 100
        for i in range(count):
            self.spikes.append(Spike(x + i * 55))

    def spawn_spear(self):
        self.spear = Spear()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if not self.game_over and not self.win:
                    if event.key in [pygame.K_SPACE, pygame.K_UP]:
                        self.player.jump()

                if (self.game_over or self.win) and event.key == pygame.K_r:
                    self.__init__()

    def update(self):
        if self.game_over or self.win:
            return

        self.player.update()

        self.spawn_timer += 1
        if self.spawn_timer >= self.next_spawn:
            self.spawn_spikes()
            self.spawn_timer = 0
            self.next_spawn = random.randint(70, 130)

        if self.score >= 150 and self.spear is None and not self.spear_taken:
            self.spawn_spear()

        if self.spear:
            self.spear.update(self.speed)

            if self.player.rect.colliderect(self.spear.rect):
                self.player.has_spear = True
                self.spear_taken = True
                self.spear = None

            elif self.spear.rect.right < 0:
                self.spear = None

        for spike in self.spikes[:]:
            spike.update(self.speed)

            if not spike.scored and spike.rect.right < self.player.rect.left:
                spike.scored = True
                self.score += 5

            if self.player.rect.colliderect(spike.rect):
                if self.player.has_spear:
                    self.player.has_spear = False
                    self.spikes.remove(spike)
                else:
                    self.game_over = True

        self.spikes = [s for s in self.spikes if s.rect.right > 0]

        self.speed += 0.001

        if self.score >= 3000:
            self.win = True

    def draw_background(self):
        for y in range(HEIGHT):
            color = (10, 10, 30 + y // 8)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        for star in stars:
            pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), star[2])
            star[0] -= self.speed / 4
            if star[0] < 0:
                star[0] = WIDTH
                star[1] = random.randint(0, HEIGHT)

        pygame.draw.circle(screen, PURPLE, (850, 80), 70)
        pygame.draw.circle(screen, BLUE, (820, 60), 20)
        pygame.draw.circle(screen, BLUE, (880, 110), 15)

        pygame.draw.rect(screen, (40, 40, 40), (0, GROUND_Y, WIDTH, HEIGHT))

    def draw_ui(self):
        t = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(t, (20, 20))

        if self.player.has_spear:
            t2 = self.font.render("SPEAR", True, WHITE)
            screen.blit(t2, (20, 60))

    def draw_end(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        if self.win:
            text = self.big_font.render("YOU WIN!", True, WHITE)
        else:
            text = self.big_font.render("GAME OVER", True, WHITE)

        score = self.font.render(f"SCORE: {self.score}", True, WHITE)
        restart = self.font.render("PRESS R", True, WHITE)

        screen.blit(text, (WIDTH//2 - text.get_width()//2, 120))
        screen.blit(score, (WIDTH//2 - score.get_width()//2, 200))
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 260))

    def draw(self):
        self.draw_background()

        self.player.draw(screen)

        for spike in self.spikes:
            spike.draw(screen)

        if self.spear:
            self.spear.draw(screen)

        self.draw_ui()

        if self.game_over or self.win:
            self.draw_end()

        pygame.display.flip()

    def run(self):
        while True:
            clock.tick(FPS)
            self.events()
            self.update()
            self.draw()


game = Game()
game.run()