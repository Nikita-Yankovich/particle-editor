import pygame
import sys
sys.path.insert(0, "..")
from Emitter import Emitter

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

"""emitter_config = {}

emitter = Emitter((400, 400), 0, 1.0, 0, emitter_config)"""

#Cam set
camPos = pygame.Vector2(0, 0)
camera_speed = 300

play = True
while play:
    # Ограничиваем FPS и получаем Delta Time (dt) в секундах
    # clock.tick(FPS) возвращает миллисекунды, делим на 1000.0
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False

    # Cam movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        camPos.x -= camera_speed * dt
    if keys[pygame.K_RIGHT]:
        camPos.x += camera_speed * dt
    if keys[pygame.K_UP]:
        camPos.y -= camera_speed * dt
    if keys[pygame.K_DOWN]:
        camPos.y += camera_speed * dt

    # Emmiter update
    """emitter.update(dt)"""

    # Draw
    window.fill((20, 20, 30))
    """emitter.draw(window, camPos)
    emitter_screen_x = int(emitter.pos.x - camPos.x)
    emitter_screen_y = int(emitter.pos.y - camPos.y)
    if 0 <= emitter_screen_x <= WIDTH and 0 <= emitter_screen_y <= HEIGHT:
        pygame.draw.circle(window, (255, 255, 255), (emitter_screen_x, emitter_screen_y), 4)"""

    pygame.display.update()

pygame.quit()
sys.exit()
