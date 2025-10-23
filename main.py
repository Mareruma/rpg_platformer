import pygame
import sys
from codes.map import GameMap
from codes.player import Player

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 300
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Kamera
class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)

    def update(self, target):
        self.offset.x = target.rect.centerx - SCREEN_WIDTH // 2
        self.offset.y = target.rect.centery - SCREEN_HEIGHT // 2


# Funkcija — savāc kolīzijas flīzes
def get_solid_tiles(map_data):
    tiles = []
    for layer in map_data.tmx_data.visible_layers:
        if hasattr(layer, "tiles"):
            for x, y, image in layer.tiles():
                if image:
                    rect = pygame.Rect(
                        x * map_data.tilewidth,
                        y * map_data.tileheight,
                        map_data.tilewidth,
                        map_data.tileheight
                    )
                    tiles.append(rect)
    return tiles


# --- Sākotnējā karte un spēlētājs ---
current_map = GameMap("level1.tmx")
player = Player(*current_map.spawn_point)
camera = Camera()

door_cooldown = 1000  # ms
last_door_use = 0

tiles = get_solid_tiles(current_map)

# --- Spēles cikls ---
running = True
while running:
    dt = clock.tick(60) / 1000
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                player.toggle_stats()

    # --- Input un fizika ---
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.apply_gravity()
    player.update(tiles, current_map.traps)  # tagad traps tiek nodots player.update()
    camera.update(player)

    # --- Miršanas pārbaude ---
    if player.hp <= 0:
        print(f"{player.name} has died!")
        running = False

    # --- Zīmēšana ---
    screen.fill((0, 0, 0))
    current_map.draw(screen, camera)
    player.draw(screen, camera)

    # --- Durvju loģika ar cooldown ---
    for door in current_map.doors:
        if player.rect.colliderect(door["rect"]):
            if door["target"] and door["pair"]:
                text = font.render("Press O to enter", True, (255, 255, 255))
                screen.blit(
                    text,
                    (
                        door["rect"].x - camera.offset.x,
                        door["rect"].y - 20 - camera.offset.y
                    )
                )

                if keys[pygame.K_o] and current_time - last_door_use >= door_cooldown:
                    last_door_use = current_time
                    new_map = GameMap(door["target"])
                    spawn = None
                    for d in new_map.doors:
                        if d["pair"] == door["pair"]:
                            spawn = d["rect"].topleft
                            break
                    player.rect.topleft = spawn if spawn else new_map.spawn_point
                    current_map = new_map
                    tiles = get_solid_tiles(current_map)
                    break

    pygame.display.flip()

pygame.quit()
sys.exit()
