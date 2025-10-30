import pygame
import sys
from codes.map import GameMap
from codes.player import Player
from codes.door_animator import DoorAnimator
from codes.gui import Button, fade

pygame.init()

# --- Settings ---
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = 500, 300
SCALE = 3
SCREEN_WIDTH, SCREEN_HEIGHT = ORIGINAL_WIDTH * SCALE, ORIGINAL_HEIGHT * SCALE

fullscreen = True
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# --- Camera ---
class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)

    def update(self, target):
        self.offset.x = target.rect.centerx - ORIGINAL_WIDTH // 2
        self.offset.y = target.rect.centery - ORIGINAL_HEIGHT // 2

# --- Helper ---
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

# --- Game Setup ---
def start_game():
    global current_map, player, camera, tiles, door_animator, transition_active, transition_data
    current_map = GameMap("starter_area.tmx")
    player = Player(*current_map.spawn_point)
    camera = Camera()
    tiles = get_solid_tiles(current_map)
    door_animator = DoorAnimator("textures/map/door-opening.png", 32, 32, fps=12)
    transition_active = False
    transition_data = {}
    fade(screen, fade_in=True)

# --- Buttons ---
menu_buttons = [
    Button(SCREEN_HEIGHT // 2 - 100, "playing", "textures/gui/start-btn.png", SCREEN_WIDTH),
    Button(SCREEN_HEIGHT // 2 + 20, None, "textures/gui/options-btn.png", SCREEN_WIDTH),
    Button(SCREEN_HEIGHT // 2 + 120, "quit", "textures/gui/quit-btn.png", SCREEN_WIDTH)
]

pause_buttons = [
    Button(SCREEN_HEIGHT // 2 - 60, "playing", "textures/gui/start-btn.png", SCREEN_WIDTH),
    Button(SCREEN_HEIGHT // 2 + 20, "menu", "textures/gui/quit-btn.png", SCREEN_WIDTH)
]

# --- Main Loop ---
game_state = "menu"
start_game()
door_cooldown = 1000
last_door_use = 0
player_slide_speed = 60
running = True

while running:
    dt = clock.tick(60) / 1000
    current_time = pygame.time.get_ticks()
    click = False
    mouse_pos = pygame.mouse.get_pos()

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = "paused" if game_state == "playing" else "playing"
            elif event.key == pygame.K_F11:
                fullscreen = not fullscreen
                screen = pygame.display.set_mode(
                    (SCREEN_WIDTH, SCREEN_HEIGHT),
                    pygame.FULLSCREEN if fullscreen else 0
                )

    # --- MENU STATE ---
    if game_state == "menu":
        screen.fill((40, 40, 60))
        title = font.render("My RPG Game", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        for btn in menu_buttons:
            result = btn.update(mouse_pos, click)
            btn.draw(screen)
            if result:
                if result == "playing":
                    start_game()
                elif result == "quit":
                    running = False
                game_state = result or game_state

    # --- PLAYING STATE ---
    elif game_state == "playing":
        keys = pygame.key.get_pressed()
        if not transition_active:
            player.handle_input(keys)
            player.apply_gravity()
            player.update(tiles, current_map.traps)
        camera.update(player)

        temp_surface = pygame.Surface((ORIGINAL_WIDTH, ORIGINAL_HEIGHT))
        temp_surface.fill((0, 0, 0))
        current_map.draw(temp_surface, camera)
        player.draw(temp_surface, camera)

        # --- Doors ---
        for door in current_map.doors:
            if player.rect.colliderect(door["rect"]) and door["target"] and door["pair"]:
                text = font.render("Press O to enter", True, (255, 255, 255))
                temp_surface.blit(text, (door["rect"].x - camera.offset.x, door["rect"].y - 20 - camera.offset.y))
                if keys[pygame.K_o] and not transition_active and current_time - last_door_use >= door_cooldown:
                    last_door_use = current_time
                    transition_active = True
                    transition_data = {"target": door["target"], "pair": door["pair"], "door_rect": door["rect"]}
                    door_animator.play(door["rect"].x, door["rect"].y)

        # --- NPCs ---
        for npc in current_map.npcs:
            if player.rect.colliderect(npc.rect) and not npc.in_dialogue:
                t_text = font.render("Press T to talk", True, (255, 255, 255))
                temp_surface.blit(t_text, (npc.rect.x - camera.offset.x, npc.rect.y - 20 - camera.offset.y))
            npc.draw_dialogue(temp_surface)

        # --- Transition ---
        if transition_active:
            door_animator.update(dt)
            door_rect = transition_data["door_rect"]
            slide_vector = pygame.Vector2(door_rect.center) - pygame.Vector2(player.rect.center)
            if slide_vector.length() > 1:
                slide_vector.scale_to_length(player_slide_speed * dt)
                player.rect.center += slide_vector
            door_animator.draw(temp_surface, camera)

            if door_animator.finished:
                fade(screen, fade_in=False)
                new_map = GameMap(transition_data["target"])
                spawn = None
                for d in new_map.doors:
                    if d["pair"] == transition_data["pair"]:
                        spawn = d["rect"].topleft
                        break
                player.rect.topleft = spawn if spawn else new_map.spawn_point
                current_map = new_map
                tiles = get_solid_tiles(current_map)
                fade(screen, fade_in=True)
                transition_active = False
                transition_data = {}

        zoomed_surface = pygame.transform.scale(temp_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(zoomed_surface, (0, 0))

    # --- PAUSED STATE ---
    elif game_state == "paused":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        pause_text = font.render("Game Paused", True, (255, 255, 255))
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 50))

        for btn in pause_buttons:
            result = btn.update(mouse_pos, click)
            btn.draw(screen)
            if result:
                if result == "menu":
                    game_state = "menu"
                elif result == "playing":
                    game_state = "playing"

    pygame.display.flip()

pygame.quit()
sys.exit()
