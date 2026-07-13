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
    'endSize': 2,
    'startSpin': 0,
    'endSpin': 0,
    # Цвет
    'start_rgba': (255, 120, 0, 255),
    'end_rgba': (150, 50, 50, 0),

    'fadeIn': 0.05,
    'fadeOut': 0.4,
    
    'max_particles': 600,
    'emission': 4 * 60,
    'duration': -1
}

# Создаем один объект класса Emitter в центре экрана (400, 400)
# Параметры: pos, rotation, scale, emitter_id, config
emitter = Emitter((400, 400), 0, 1.0, 0, fire_config)

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
    emitter.update(dt)

    # Draw
    window.fill((20, 20, 30))
    emitter.draw(window, camPos)
    emitter_screen_x = int(emitter.pos.x - camPos.x)
    emitter_screen_y = int(emitter.pos.y - camPos.y)
    if 0 <= emitter_screen_x <= WIDTH and 0 <= emitter_screen_y <= HEIGHT:
        pygame.draw.circle(window, (255, 255, 255), (emitter_screen_x, emitter_screen_y), 4)

    pygame.display.update()

pygame.quit()
sys.exit()
