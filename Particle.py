import pygame
import math

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
        # Округляем радиус частицы (минимальный размер — 1 пиксель)
        radius = max(1, int(self.size))
        # ПЕРЕВОД В ЭКРАННЫЕ КООРДИНАТЫ: вычитаем позицию камеры
        center_x = int(self.pos[0] - camPos[0])
        center_y = int(self.pos[1] - camPos[1])
        # Оптимизация (Culling): если частица за пределами экрана, не тратим ресурсы на рисование
        screen_w, screen_h = surface.get_size()
        if (center_x + radius < 0 or center_x - radius > screen_w or
            center_y + radius < 0 or center_y - radius > screen_h):
            return

        r = max(0, min(255, int(self.rgba[0])))
        g = max(0, min(255, int(self.rgba[1])))
        b = max(0, min(255, int(self.rgba[2])))
        alpha = max(0, min(255, int(self.rgba[3])))
        
        # Рисуем через прозрачную поверхность, чтобы работал Alpha-канал (fadeIn / fadeOut)
        particle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (r, g, b, alpha), (radius, radius), radius)
        
        # Отрисовка на экран со смещением на радиус (чтобы центр круга совпал с center_x/y)
        if hasattr(self, 'blending') and self.blending:
            # Color Blending
            a_factor = alpha / 255.0
            r = int(r * a_factor)
            g = int(g * a_factor)
            b = int(b * a_factor)
            
            # Рисуем круг (на аддитивном слое альфа-канал самого блендинга зануляется)
            pygame.draw.circle(particle_surf, (r, g, b, 0), (radius, radius), radius)
            surface.blit(particle_surf, (center_x - radius, center_y - radius), special_flags=pygame.BLEND_RGB_ADD)
        else:
            # Обычная отрисовка (просто перекрытие пикселей на своем слое)
            surface.blit(particle_surf, (center_x - radius, center_y - radius))


