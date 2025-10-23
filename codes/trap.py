import pygame, time

class Trap:
    def __init__(self, x, y, width, height, damage, damage_speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.damage = damage
        self.damage_speed = damage_speed
        self.last_hit_time = 0

    def check_collision(self, player):
        current_time = time.time()
        if self.rect.colliderect(player.rect):
            interval = max(0.1, 1.0 / self.damage_speed)
            if current_time - self.last_hit_time > interval:
                player.take_damage(self.damage)
                self.last_hit_time = current_time

    def draw(self, screen, camera):
        pygame.draw.rect(screen, (200, 50, 50), (self.rect.x - camera.x, self.rect.y - camera.y, self.rect.width, self.rect.height), 2)
