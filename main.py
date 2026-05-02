import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Python")

clock = pygame.time.Clock()

run_frames = []
for i in range(1, 16):
    img = pygame.image.load(f"run{i}.png")
    img = pygame.transform.scale(img, (50, 50))
    run_frames.append(img)

spike_img = pygame.image.load("spike.png")
spike_img = pygame.transform.scale(spike_img, (40, 40))

spear_img = pygame.image.load("spear.png")
spear_img = pygame.transform.scale(spear_img, (30, 30))

player = pygame.Rect(50, 200, 50, 50)
dy = 0
gravity = 0.6
jumping = False

frame = 0
frame_timer = 0

has_spear = False

spikes = []
spear = None

score = 0

def spawn_spike():
    spikes.append(pygame.Rect(WIDTH, 220, 40, 40))

def spawn_spear():
    global spear
    spear = pygame.Rect(WIDTH, 210, 30, 30)

while True:
    clock.tick(60)
    screen.fill((20, 20, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_UP]:
                if not jumping:
                    dy = -12
                    jumping = True

    dy += gravity
    player.y += dy

    if player.y >= 200:
        player.y = 200
        jumping = False

    frame_timer += 1
    if frame_timer > 5:
        frame = (frame + 1) % 15
        frame_timer = 0

    if random.random() < 0.02:
        spawn_spike()

    for s in spikes:
        s.x -= 5

    spikes = [s for s in spikes if s.x > -50]

    for s in spikes[:]:
        if player.colliderect(s):
            if has_spear:
                spikes.remove(s)
                has_spear = False
            else:
                print("Game Over! Score:", score)
                pygame.quit()
                sys.exit()

    if score == 250:
        spawn_spear()

    if spear:
        spear.x -= 5

        if player.colliderect(spear):
            has_spear = True
            spear = None

        if spear and spear.x < -50:
            spear = None

    score += 1

    screen.blit(run_frames[frame], (player.x, player.y))

    for s in spikes:
        screen.blit(spike_img, (s.x, s.y))

    if spear:
        screen.blit(spear_img, (spear.x, spear.y))

    font = pygame.font.SysFont(None, 30)
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (650, 10))

    if has_spear:
        text2 = font.render("Spear: YES", True, (255, 255, 255))
        screen.blit(text2, (650, 40))

    pygame.display.flip()