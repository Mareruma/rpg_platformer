import pygame

# --- GUI Button class ---
class Button:
    def __init__(self, y, action, image_path, screen_width):
        self.action = action
        self.hovered = False
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=(screen_width // 2, y))

    def draw(self, surf):
        img = self.image.copy()
        if self.hovered:
            img.set_alpha(220)
        surf.blit(img, self.rect)

    def update(self, mouse_pos, click):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and click:
            return self.action
        return None

# --- Helper functions ---
def fade(screen, fade_in=True, speed=5):
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill((0, 0, 0))
    for alpha in (range(0, 255, speed) if fade_in else range(255, 0, -speed)):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)
