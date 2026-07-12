import pygame
import sys
sys.path.insert(0, "..")
from Emitter import Emitter

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

fire_config = {
    'posVarX': 15,
    'posVarY': 5,
    'lifetime': 1.8,
    'angle': -90,
    'angleVar': 20, 
    'speed': 250,
    # Физика
    'gravityX': 0,
    'gravityY': 180,
    'accelRad': 0,
    'accelTan': 0,
    # Трение
    'frictionP': 0.1,
    'frictionS': 0.0,
    'frictionR': 0.0,
    # Размеры (Старт -> Конец)
    'startSize': 14,
    'endSize': 16,
    'startSpin': 0,
    'endSpin': 16,
    # Цвет
    'start_rgba': (255, 120, 0, 255),
    'end_rgba': (150, 50, 50, 0),

    'fadeIn': 0.05,
    'fadeOut': 0.4,

    'max_particles': 600,
    'emission': 4,
    'duration': -1
}

# Создаем один объект класса Emitter в центре экрана (400, 400)
# Параметры: pos, rotation, scale, emitter_id, config
emitter = Emitter((400, 400), 0, 1.0, 0, fire_config)

# config1: Fire1
orange_config = fire_config.copy()
orange_config['start_rgba'] = (255, 0, 0, 255)
orange_config['end_rgba'] = (255, 0, 20, 0)
orange_config['startSize'] = 16
orange_config['blending'] = True

# config2: Fire2
yellow_config = fire_config.copy()
yellow_config['start_rgba'] = (0, 220, 0, 255)
yellow_config['end_rgba'] = (0, 220, 0, 0)
yellow_config['startSize'] = 16
yellow_config['blending'] = True 

emitter_orange = Emitter((400, 400), 0, 1.0, 0, orange_config)
emitter_yellow = Emitter((400, 400), 0, 1.0, 1, yellow_config)

camPos = pygame.Vector2(0, 0)
camera_speed = 300

play = True
while play:
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

    # Emitters update
    emitter_orange.update(dt)
    emitter_yellow.update(dt)

    window.fill((20, 20, 30))

    # Layer1
    fire_layer = pygame.Surface((WIDTH, HEIGHT))
    fire_layer.fill((0, 0, 0))  # Черный цвет станет прозрачным при блите

    emitter_yellow.draw(fire_layer, camPos)
    emitter_orange.draw(fire_layer, camPos)

    #Output layer
    window.blit(fire_layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    pygame.display.update()

pygame.quit()
sys.exit()
