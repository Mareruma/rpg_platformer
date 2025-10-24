import pygame
import os
from codes.player_stats import PlayerStats

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 32)
        self.vel = pygame.Vector2(0, 0)
        self.speed = 2
        self.jump_strength = 6
        self.gravity = 0.3
        self.on_ground = False
        self.facing_right = True  # True = skata pa labi, False = pa kreisi

        # Statistika
        self.stats = PlayerStats()
        self.hp = self.stats.hp
        self.damage = self.stats.damage
        self.name = self.stats.name
        self.char_class = self.stats.char_class
        self.level = self.stats.level
        self.spells = self.stats.get_spell_list()

        # Ielādē attēlu pēc klases nosaukuma
        image_path = os.path.join("textures", "character", f"{self.char_class.lower()}.png")
        if os.path.exists(image_path):
            self.original_image = pygame.image.load(image_path).convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (self.rect.width, self.rect.height))
            self.image = self.original_image
        else:
            self.image = None
            print(f"Warning: Image not found at {image_path}")

        # GUI
        self.show_stats = False
        self.font = pygame.font.SysFont("consolas", 18)
        self.alive = True

    def handle_input(self, keys):
        self.vel.x = 0
        if keys[pygame.K_a]:
            self.vel.x = -self.speed
            self.facing_right = False
        if keys[pygame.K_d]:
            self.vel.x = self.speed
            self.facing_right = True
        if keys[pygame.K_w] and self.on_ground:
            self.vel.y = -self.jump_strength
            self.on_ground = False

    def apply_gravity(self):
        self.vel.y += self.gravity
        if self.vel.y > 10:
            self.vel.y = 10

    def update(self, tiles, traps):
        # X kustība
        self.rect.x += self.vel.x
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vel.x > 0:
                    self.rect.right = tile.left
                elif self.vel.x < 0:
                    self.rect.left = tile.right

        # Y kustība
        self.rect.y += self.vel.y
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vel.y > 0:
                    self.rect.bottom = tile.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = tile.bottom
                    self.vel.y = 0

        # Pieskaršanās slazdiem
        current_time = pygame.time.get_ticks()
        for trap in traps:
            if self.rect.colliderect(trap["rect"]):
                if "last_hit" not in trap:
                    trap["last_hit"] = 0
                interval = 1000 / trap["damage_speed"]  # damage-speed ir hits per sec
                if current_time - trap["last_hit"] >= interval:
                    self.take_damage(trap["damage"])
                    trap["last_hit"] = current_time

        # Atjauno attēlu atkarībā no skatīšanās virziena
        if self.image and not self.facing_right:
            self.image = pygame.transform.flip(self.original_image, True, False)
        elif self.image and self.facing_right:
            self.image = self.original_image

    def take_damage(self, amount):
        """Samazina HP un pārbauda nāvi"""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def toggle_stats(self):
        self.show_stats = not self.show_stats

    def draw(self, screen, camera):
        draw_pos = self.rect.move(-camera.offset.x, -camera.offset.y)
        if self.image:
            screen.blit(self.image, draw_pos)
        else:
            pygame.draw.rect(screen, (255, 0, 0), draw_pos)

        if self.show_stats:
            self.draw_stats_gui(screen)
        self.draw_hp_bar(screen)
        if not self.alive:
            self.draw_death_message(screen)

    def draw_stats_gui(self, screen):
        lines = [
            f"Name: {self.name}",
            f"Class: {self.char_class}",
            f"Level: {self.level}",
            f"HP: {self.hp}",
            f"Damage: {self.damage}",
            f"Damage type: {', '.join(self.stats.damage_type)}",
            f"Armor: {', '.join(self.stats.armor)}",
            "",
            "Spells:"
        ]
        for spell in self.spells:
            lines.append(f" - {spell['name']} ({spell['effect']})")

        line_height = self.font.get_height() + 2
        gui_height = (len(lines) * line_height) + 20
        gui_width = 10 + max(self.font.size(line)[0] for line in lines) + 20
        x, y = 40, 40

        s = pygame.Surface((gui_width, gui_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (x, y))
        pygame.draw.rect(screen, (200, 200, 200), (x, y, gui_width, gui_height), 2)

        for i, line in enumerate(lines):
            text = self.font.render(line, True, (255, 255, 255))
            screen.blit(text, (x + 10, y + 10 + i * line_height))

    def draw_hp_bar(self, screen):
        bar_width = 200
        bar_height = 20
        x, y = 20, 20
        pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
        hp_ratio = max(self.hp / self.stats.hp, 0)
        pygame.draw.rect(screen, (200, 0, 0), (x, y, bar_width * hp_ratio, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

    def draw_death_message(self, screen):
        font = pygame.font.SysFont("consolas", 48, bold=True)
        text = font.render("YOU DIED", True, (255, 0, 0))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, text_rect)
