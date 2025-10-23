import pygame

class Camera:
    def __init__(self, width, height):
        self.offset = pygame.Vector2(0, 0)
        self.width = width
        self.height = height

    def follow(self, target):
        self.offset.x = target.rect.centerx - self.width // 2
        self.offset.y = target.rect.centery - self.height // 2

        if self.offset.x < 0: self.offset.x = 0
        if self.offset.y < 0: self.offset.y = 0
