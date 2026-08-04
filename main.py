import pygame
import sys
# sys.path.insert(0, "..")
# from Emitter import Emitter
from SceneManager import SceneManager

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

"""emitter_config = {}

emitter = Emitter((400, 400), 0, 1.0, 0, emitter_config)"""

# Scene system initialization
scene_manager = SceneManager()
scene_manager.open_scene("saves/vortex_with_sprites_scene.json")
# Создаем один многоразовый промежуточный холст для изоляции blending всей сцены
scene_surface = pygame.Surface((WIDTH, HEIGHT))

# Cam set
camPos = pygame.Vector2(0, 0)
camera_speed = 300

play = True
while play:
    # Ограничиваем FPS и получаем Delta Time (dt) в секундах
    # clock.tick(FPS) возвращает миллисекунды, делим на 1000.0
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        # TODO(UI): красный крестик окна и Alt+F4 должны открывать одно и то же окно подтверждения выхода. Клавиша Esc
        # в главном меню должна вызывать это же окно. Приложение и открытая сцена закрываются только после
        # решения пользователя.
        if event.type == pygame.QUIT: play = False

    # Cam movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: camPos.x -= camera_speed * dt
    if keys[pygame.K_RIGHT]: camPos.x += camera_speed * dt
    if keys[pygame.K_UP]: camPos.y -= camera_speed * dt
    if keys[pygame.K_DOWN]: camPos.y += camera_speed * dt

    # Scene update
    scene_manager.update(dt)

    # Draw
    window.fill((20, 20, 30))
    scene_manager.draw(scene_surface, camPos)
    window.blit(scene_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    pygame.display.update()

pygame.quit()
scene_manager.close_scene()
""" ^^^ Удалить это когда будет добавлен UI (закрытие не через кнопку будет считаться внештатным)"""
sys.exit()
