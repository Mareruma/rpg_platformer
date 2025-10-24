import pygame
from pytmx.util_pygame import load_pygame
import os

class GameMap:
    def __init__(self, filename):
        self.filename = filename
        self.load_map()

    def load_map(self):
        from codes.npc import NPC  # Importē šeit, lai izvairītos no cikliskas importēšanas
        # Ielādē TMX failu
        self.tmx_data = load_pygame(os.path.join("maps", self.filename))
        self.tilewidth = self.tmx_data.tilewidth
        self.tileheight = self.tmx_data.tileheight

        # Datu struktūras
        self.spawn_point = (100, 100)
        self.doors = []
        self.traps = []
        self.npcs = []

        # Objektu lasīšana
        for obj in self.tmx_data.objects:
            # Spawna punkts
            if obj.type == "PlayerSpawn":
                self.spawn_point = (int(obj.x), int(obj.y))

            # Durvis
            elif obj.type == "Door":
                rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
                props = getattr(obj, "properties", {}) or {}
                pair = props.get("pair")
                target = props.get("target")
                self.doors.append({
                    "rect": rect,
                    "pair": pair,
                    "target": target
                })

            # Trap
            elif obj.type == "Trap":
                rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
                props = getattr(obj, "properties", {}) or {}
                damage = float(props.get("damage", 1))
                damage_speed = float(props.get("damage-speed", 1))
                self.traps.append({
                    "rect": rect,
                    "damage": damage,
                    "damage_speed": damage_speed,
                    "last_hit": 0
                })

            # NPC
            elif obj.type and obj.type.startswith("npc"):
                npc = NPC(obj)
                self.npcs.append(npc)

    def draw(self, screen, camera):
        # Tiles layeri
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, image in layer.tiles():
                    if image:
                        screen.blit(
                            image,
                            (x * self.tilewidth - camera.offset.x,
                             y * self.tileheight - camera.offset.y)
                        )

        # Object layeri — vizuālie elementi
        for obj in self.tmx_data.objects:
            rect = pygame.Rect(
                obj.x, obj.y,
                getattr(obj, "width", 32),
                getattr(obj, "height", 32)
            )
            rect.topleft = (rect.x - camera.offset.x, rect.y - camera.offset.y)

            if obj.type == "Trap":
                trap_image = pygame.image.load("textures/map/trap.png").convert_alpha()
                trap_image = pygame.transform.scale(trap_image, (int(obj.width), int(obj.height)))
                screen.blit(trap_image, (obj.x - camera.offset.x, obj.y - camera.offset.y))
            elif obj.type == "Door":
                door_image = pygame.image.load("textures/map/door.png").convert_alpha()
                door_image = pygame.transform.scale(door_image, (int(obj.width), int(obj.height)))
                screen.blit(door_image, (obj.x - camera.offset.x, obj.y - camera.offset.y))
            elif obj.type == "PlayerSpawn":
                pygame.draw.rect(screen, (0, 0, 255), rect, 2)

        # NPC zīmēšana
        for npc in self.npcs:
            npc.draw(screen, camera)