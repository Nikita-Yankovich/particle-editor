import pygame
import sys
sys.path.insert(0, "..")
from Emitter import Emitter

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

vortex_config = {
    'posVarX': 0,
    'posVarY': 0,
    'lifetime': 3.5,
    'angle': 0,
    'angleVar': 180,
    'speed': 40,
    # ВИХРЕВАЯ ФИЗИКА
    'gravityX': 0,
    'gravityY': 0,
    'accelRad': -20,
    'accelTan': 280,
    # Трение
    'frictionP': 0.05,
    'frictionS': 0.0,
    'frictionR': 0.0,
    # Размеры (Старт -> Конец)
    'startSize': 8,
    'endSize': 1,
    'startSpin': 0,
    'endSpin': 0,
    # Цвет
    'start_rgba': (150, 0, 255, 255),
    'end_rgba': (0, 200, 255, 0),
    # Текстура (Спрайт/Фигура)
    'is_sprite': False,
    'figure': 'circle', #variations: 'circle', square', ...
    'sprite_picture': 'spark.png',

    'fadeIn': 0.1,           
    'fadeOut': 0.5,

    'max_particles': 600,    
    'emission': 600
}

# Два одинаковых эмиттера в центре экрана (400, 300) для эффекта blending
vortex_config_bg = vortex_config.copy()
vortex_config_bg['blending'] = False

vortex_config_core = vortex_config.copy()
vortex_config_core['start_rgba'] = (0, 255, 200, 255)
#vortex_config_core['end_rgba'] = (0, 50, 100, 0)
vortex_config_core['startSize'] = 4
vortex_config_core['blending'] = True

emitter_bg = Emitter((400, 300), 0, 1.0, 0, vortex_config_bg)
emitter_core = Emitter((400, 300), 0, 1.0, 1, vortex_config_core)

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
    emitter_bg.update(dt)
    emitter_core.update(dt)

    window.fill((10, 10, 15))

    # Layer1
    fire_layer = pygame.Surface((WIDTH, HEIGHT))
    fire_layer.fill((0, 0, 0))  
    
    emitter_bg.draw(fire_layer, camPos)
    emitter_core.draw(fire_layer, camPos)

    # Ouput layer
    window.blit(fire_layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    pygame.display.update()

pygame.quit()
sys.exit()
