import pygame
import math
import pygame.gfxdraw

class Particle:
    def __init__(self, config):
        self.parrent = config['emitter_id']
        
        # 1. Start Pos
        self.pos = (config['posX'], config['posY'])
        
        # 2. Lifetime Set
        self.lifetime = config['lifetime']
        self.age = 0.0
        
        # 3. Movement properties: speed & direction -> speedX & speedY
        angle_rad = math.radians(config['actual_angle']) 
        self.vx = config['speed'] * math.cos(angle_rad)
        self.vy = config['speed'] * math.sin(angle_rad)

        # Spin
        self.startSpin = config.get('startSpin', 0)
        self.endSpin = config.get('endSpin', 0)
        self.spin = config.get('startSpin', 0)
        
        # Phisics properties: grsvity & friction
        self.gravityX = config['gravityX']
        self.gravityY = config['gravityY']
        self.frictionP = config['frictionP']

        self.startX = config['posX'] # Центр эмиттера в момент рождения
        self.startY = config['posY']
        self.accelRad = config.get('accelRad', 0.0)
        self.accelTan = config.get('accelTan', 0.0)
        
        # 4. Visuals Set
        self.startSize = config['startSize']
        self.size = config['startSize']
        self.endSize = config['endSize']

        self.start_color = config['start_rgba']
        self.end_color = config['end_rgba'] 
        
        self.rgba = list(config['start_rgba'])
        self.end_rgba = config['end_rgba']

        self.fadeIn = config['fadeIn']
        self.fadeOut = config['fadeOut']

        self.blending = config.get('blending', False)

        self.is_sprite = config.get('is_sprite', False)
        self.figure = config.get('figure', 'circle')
        if self.is_sprite:
            try: # Загружаем спрайт с поддержкой прозрачности
                self.raw_sprite = pygame.image.load(config['sprite_picture']).convert_alpha()
            except Exception: # Если файл не найден, создаем белую заглушку 10х10
                self.raw_sprite = pygame.Surface((10, 10), pygame.SRCALPHA)
                self.raw_sprite.fill((255, 255, 255, 255))

    def update(self, dt):
        # 1. Aging
        self.age += dt
        if self.age >= self.lifetime:
            return False
            
        # Рассчитываем прогресс жизни от 0.0 (рождение) до 1.0 (смерть)
        life_ratio = self.age / self.lifetime
        
        # 2. Movement: Physics (Gravity, Acceleration)
        # accelRad & accelTan
        dx = self.pos[0] - self.startX
        dy = self.pos[1] - self.startY
        distance = math.sqrt(dx*dx + dy*dy)
        if distance == 0: 
            distance = 0.0001 # Защита от деления на ноль в самый первый кадр
            
        # Нормализуем вектор (получаем чистые направления по осям)
        dir_x = dx / distance
        dir_y = dy / distance
        
        # Радиальная сила (толкает от центра наружу или тянет внутрь)
        rad_x = dir_x * self.accelRad
        rad_y = dir_y * self.accelRad
        
        # Тангенциальная сила (перпендикулярный вектор, закручивающий в вихрь)
        tan_x = -dir_y * self.accelTan
        tan_y = dir_x * self.accelTan

        # Складываем все силы, получаем результирующую силу (ускорение -> изменение скорости)
        self.vx += (self.gravityX + rad_x + tan_x) * dt
        self.vy += (self.gravityY + rad_y + tan_y) * dt
        
        # Movement: friction (frictionP)
        self.vx *= (1.0 - self.frictionP * dt)
        self.vy *= (1.0 - self.frictionP * dt)

        # Coordinates update (переводим кортеж в новые значения)
        new_x = self.pos[0] + self.vx * dt
        new_y = self.pos[1] + self.vy * dt
        self.pos = (new_x, new_y)
        
        # 3. Visuals changes (Размер уменьшается/увеличивается к концу жизни)
        self.size = self.startSize + (self.endSize - self.startSize) * life_ratio
        self.spin = self.startSpin + (self.endSpin - self.startSpin) * life_ratio

        # Color (Линейно меняем R, G, B из стартового в конечный)
        for i in range(3):  # Меняем только RGB компоненты
            self.rgba[i] = self.start_color[i] + (self.end_color[i] - self.start_color[i]) * life_ratio
            
        # 5. Alpha (Альфа-канал) с учетом fadeIn и fadeOut
        # Сначала считаем базовую альфу для текущего момента жизни
        base_alpha = self.start_color[3] + (self.end_color[3] - self.start_color[3]) * life_ratio

        if life_ratio < self.fadeIn and self.fadeIn > 0:
            # Плавное появление (от 0 до базовой альфы)
            self.rgba[3] = base_alpha * (life_ratio / self.fadeIn)
        elif life_ratio > (1.0 - self.fadeOut) and self.fadeOut > 0:
            # Плавное исчезновение в конце жизни
            remaining_ratio = (1.0 - life_ratio) / self.fadeOut
            self.rgba[3] = base_alpha * remaining_ratio
        else:
            self.rgba[3] = base_alpha

        return True  # Частица всё еще жива

    def draw(self, surface, camPos):
        size = max(1, int(self.size))
        center_x = int(self.pos[0] - camPos.x)
        center_y = int(self.pos[1] - camPos.y)
        
        # Проверка границ экрана (Culling)
        screen_w, screen_h = surface.get_size()
        if (center_x + size < 0 or center_x - size > screen_w or
            center_y + size < 0 or center_y - size > screen_h):
            return

        # color calculating
        r = max(0, min(255, int(self.rgba[0])))
        g = max(0, min(255, int(self.rgba[1])))
        b = max(0, min(255, int(self.rgba[2])))
        alpha = max(0, min(255, int(self.rgba[3])))
        # Применяем Premultiplied Alpha, если включен blending
        if hasattr(self, 'blending') and self.blending:
            a_factor = alpha / 255.0
            r, g, b = int(r * a_factor), int(g * a_factor), int(b * a_factor)
            draw_alpha = 255
        else:
            draw_alpha = alpha

        # ЛОГИКА ОТРИСОВКИ РАЗНЫХ ТИПОВ ЧАСТИЦ
        if self.is_sprite:
            # Variant A: sprite with texture
            # 1. Sprite scaling
            scaled_sprite = pygame.transform.scale(self.raw_sprite, (size * 2, size * 2))
            
            # 2. Color mask
            color_surf = pygame.Surface(scaled_sprite.get_size(), pygame.SRCALPHA)
            color_surf.fill((r, g, b, draw_alpha))
            
            # 3. Color toning
            scaled_sprite.blit(color_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # 4. Sprite rotation (angle self.spin)
            current_spin = getattr(self, 'spin', 0)
            rotated_sprite = pygame.transform.rotate(scaled_sprite, current_spin)
            
            # Отрисовка по центру
            rect = rotated_sprite.get_rect(center=(center_x, center_y))
            if hasattr(self, 'blending') and self.blending:
                surface.blit(rotated_sprite, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)
            else:
                surface.blit(rotated_sprite, rect.topleft)
        else:
            # Variant B: geometric primitive
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            if self.figure == 'circle':
                # Используем gfxdraw для Anti-aliasing (сглаживания краев)
                # Рисуем сглаженную рамку круга, а затем заливаем его центр
                pygame.gfxdraw.aacircle(particle_surf, size, size, size - 1, (r, g, b, draw_alpha))
                pygame.gfxdraw.filled_circle(particle_surf, size, size, size - 1, (r, g, b, draw_alpha))
            elif self.figure == 'square':
                # Создаем холст с запасом под размер для спина (умножаем на 3)
                surf_size = size * 3
                particle_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                # Рисуем квадрат строго ПО ЦЕНТРУ этого холста
                # Смещаем координаты начала отрисовки на половину размера
                start_xy = surf_size // 2 - size
                pygame.draw.rect(particle_surf, (r, g, b, draw_alpha), (start_xy, start_xy, size * 2, size * 2))
                # Вращаем холст вокруг его центра
                current_spin = getattr(self, 'spin', 0)
                if current_spin != 0:
                    particle_surf = pygame.transform.rotate(particle_surf, current_spin)
                # Пересчитываем геометрию от уже повернутого расширенного холста
                rect = particle_surf.get_rect(center=(center_x, center_y))
                
            # Блитим готовый примитив на слой
            rect = particle_surf.get_rect(center=(center_x, center_y))
            if hasattr(self, 'blending') and self.blending:
                surface.blit(particle_surf, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)
            else:
                surface.blit(particle_surf, rect.topleft)

        """
        if self.is_sprite:
            # Variant A: sprite with texture
            scaled_sprite = pygame.transform.scale(self.raw_sprite, (size * 2, size * 2))
            color_surf = pygame.Surface(scaled_sprite.get_size(), pygame.SRCALPHA)
            color_surf.fill((r, g, b, draw_alpha))
            scaled_sprite.blit(color_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            rotated_sprite = pygame.transform.rotate(scaled_sprite, self.spin)
            rect = rotated_sprite.get_rect(center=(center_x, center_y))
            if hasattr(self, 'blending') and self.blending:
                surface.blit(rotated_sprite, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)
            else:
                surface.blit(rotated_sprite, rect.topleft)

        else:
            # Variant B: geometric primitive
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            if self.figure == 'circle':
                pygame.gfxdraw.aacircle(particle_surf, size, size, size - 1, (r, g, b, draw_alpha))
                pygame.gfxdraw.filled_circle(particle_surf, size, size, size - 1, (r, g, b, draw_alpha))
            
            elif self.figure == 'square':
                pygame.draw.rect(particle_surf, (r, g, b, draw_alpha), (0, 0, size * 2, size * 2))
                if self.spin != 0:
                    particle_surf = pygame.transform.rotate(particle_surf, self.spin)
            
            rect = particle_surf.get_rect(center=(center_x, center_y))
            if hasattr(self, 'blending') and self.blending:
                surface.blit(particle_surf, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)
            else:
                surface.blit(particle_surf, rect.topleft)"""
