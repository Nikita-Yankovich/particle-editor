import pygame
import random
import math
from Particle import Particle

class Emitter:
    def __init__ (self, pos, rotation, scale, emitter_id, config):
        self.id = emitter_id

        self.config = config # Запоминание config
        self.particles = []  # Список частиц этого эмиттера
        
        # 1. Emitter: Pos + PosVar, Rotation, Size
        self.emit_counter = 0.0
        self.pos = pygame.Vector2(pos[0], pos[1])
        self.rot = rotation
        self.size = scale
        
        # 2. Lifetime
        self.lifetime = config.get('lifetime', -1)
        self.duration = config.get('duration', -1)
        self.age = 0.0
        
        # 3. Movement
        angle_rad = math.radians(config['angle'])
        self.vx = config['speed'] * math.cos(angle_rad)
        self.vy = config['speed'] * math.sin(angle_rad)
        
        # Phisics
        self.gravityX = config['gravityX']
        self.gravityY = config['gravityY']
        self.accelRad = config['accelRad']  # Радиальное ускорение (от центра)
        self.accelTan = config['accelTan']  # Тангенциальное ускорение (перпендикулярно)
        
        # Friction: P - pos/speed, S - size, R - rotation)
        self.frictionP = config['frictionP']
        self.frictionS = config['frictionS']
        self.frictionR = config['frictionR']
        
        # 4. Size and Spin(Start -> End)
        self.startSize = config['startSize']
        self.endSize = config['endSize']
        self.size = self.startSize
        
        self.startSpin = config['startSpin']
        self.endSpin = config['endSpin']
        self.spin = self.startSpin

        # 5. Color (RGBA)
        self.start_color = config['start_rgba']  # Кортеж (R, G, B, A)
        self.end_color = config['end_rgba']      # Кортеж (R, G, B, A)
        self.rgba = list(self.start_color)
        
        # Fade in / out
        self.fadeIn = config['fadeIn']    # Время плавного появления (от 0 до 1)
        self.fadeOut = config['fadeOut']  # Время плавного исчезновения в конце (от 0 до 1)

    def update(self, dt):
        # 1. Emmiter aging
        self.age += dt
        
        # Если у эмиттера есть конечное время жизни (duration) и оно истекло — перестаём спавнить
        can_spawn = True
        if self.duration > 0:
            if self.age >= self.duration:
                can_spawn = False
                # Если эмиттер бесконечный или еще жив, двигаем его самого:
                # self.vx += self.gravityX * dt ... (если нужно, чтобы сам эмиттер летал)

        # 2. New particles generation
        if can_spawn:
            emission_rate = self.config.get('emission', 4.0) # измеряется: число рождений в секунду
            max_particles = self.config.get('max_particles', 400)

            time_between_emits = 1.0 / emission_rate

            # Накапливаем прошедшее реальное время (dt)
            self.emit_counter += dt

            # Пока накопилось достаточно времени для создания частиц — создаем их
            while self.emit_counter >= time_between_emits:
                self.emit_counter -= time_between_emits # Списываем "стоимость" одной частицы

                if len(self.particles) < max_particles:
                    particle_config = self.config.copy()
                    particle_config['emitter_id'] = self.id
                    particle_config['posX'] = self.pos.x + random.uniform(-self.config['posVarX'], self.config['posVarX'])
                    particle_config['posY'] = self.pos.y + random.uniform(-self.config['posVarY'], self.config['posVarY'])

                    var_angle = self.config.get('angleVar', 0)
                    particle_config['actual_angle'] = self.config['angle'] + random.uniform(-var_angle, var_angle)

                    new_particle = Particle(particle_config)
                    self.particles.append(new_particle)


        # 3. Update particles
        # Подсчёт живых частиц и очистка мёртвых
        alive_particles = []
        for particle in self.particles:
            if particle.update(dt):
                alive_particles.append(particle)
        self.particles = alive_particles

    def draw(self, surface, camPos):
        # Передаем камеру в каждую частицу (частица рисуется только если она видна)
        for particle in self.particles:
            particle.draw(surface, camPos)


