import pygame

class DoorAnimator:
    def __init__(self, image_path, frame_w, frame_h, fps=10):
        self.sprite_sheet = pygame.image.load(image_path).convert_alpha()
        self.frames = []
        self.load_frames(frame_w, frame_h)
        self.image = self.frames[0]
        self.current_frame = 0
        self.timer = 0
        self.fps = fps
        self.playing = False
        self.finished = False
        self.rect = pygame.Rect(0, 0, frame_w, frame_h)

    def load_frames(self, w, h):
        sheet_width, sheet_height = self.sprite_sheet.get_size()
        for x in range(0, sheet_width, w):
            frame = self.sprite_sheet.subsurface((x, 0, w, h))
            self.frames.append(frame)

    def play(self, x, y):
        self.playing = True
        self.finished = False
        self.current_frame = 0
        self.rect.topleft = (x, y)

    def update(self, dt):
        if not self.playing or self.finished:
            return
        self.timer += dt * 1000  # dt = sekundes
        if self.timer >= 1000 / self.fps:
            self.timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.current_frame = len(self.frames) - 1
                self.finished = True
            self.image = self.frames[self.current_frame]

    def draw(self, screen, camera):
        if self.playing:
            screen.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))


# ---------------------------
# VIENKĀRŠA FADE FUNKCIJA
# ---------------------------
def fade(screen, fade_in=True, speed=5):
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill((0, 0, 0))

    for alpha in (range(0, 255, speed) if fade_in else range(255, 0, -speed)):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)
